"""
Kafka Consumer Example using Dapr Pub/Sub
Subscribes to task events and processes them idempotently
"""

from flask import Flask, request, jsonify
from cloudevents.http import from_http
import logging
import redis

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis for idempotency tracking
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
PROCESSED_TTL = 86400  # 24 hours


@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    """Tell Dapr which topics to subscribe to"""
    subscriptions = [
        {
            'pubsubname': 'kafka-pubsub',
            'topic': 'task-events',
            'route': '/task-events'
        }
    ]
    return jsonify(subscriptions)


@app.route('/task-events', methods=['POST'])
def handle_task_event():
    """Handle task lifecycle events"""
    try:
        # Parse CloudEvent
        event = from_http(request.headers, request.get_data())

        event_id = event['id']
        event_type = event['type']
        event_data = event.data

        logger.info(f"Received event: {event_id}, type: {event_type}")

        # Idempotency check
        if is_already_processed(event_id):
            logger.info(f"Event {event_id} already processed, skipping")
            return jsonify({'status': 'SUCCESS'})

        # Route to appropriate handler
        if event_type == 'com.todoapp.task.created':
            handle_task_created(event_data)
        elif event_type == 'com.todoapp.task.completed':
            handle_task_completed(event_data)
        elif event_type == 'com.todoapp.task.updated':
            handle_task_updated(event_data)
        elif event_type == 'com.todoapp.task.deleted':
            handle_task_deleted(event_data)
        else:
            logger.warning(f"Unknown event type: {event_type}")

        # Mark as processed
        mark_as_processed(event_id)

        logger.info(f"Event {event_id} processed successfully")
        return jsonify({'status': 'SUCCESS'})

    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True)
        # Return RETRY for transient errors, DROP for permanent errors
        return jsonify({'status': 'RETRY'}), 500


def is_already_processed(event_id: str) -> bool:
    """Check if event was already processed (idempotency)"""
    return redis_client.exists(f"processed:{event_id}") == 1


def mark_as_processed(event_id: str):
    """Mark event as processed with TTL"""
    redis_client.setex(f"processed:{event_id}", PROCESSED_TTL, "1")


def handle_task_created(data: dict):
    """Process task.created event"""
    task_id = data['task_id']
    user_id = data['user_id']
    title = data['title']

    logger.info(f"Task created: {task_id} by user {user_id}: {title}")

    # Add your business logic here
    # Example: Send welcome notification, initialize analytics, etc.


def handle_task_completed(data: dict):
    """Process task.completed event"""
    task_id = data['task_id']
    user_id = data['user_id']
    is_recurring = data.get('is_recurring', False)

    logger.info(f"Task completed: {task_id} by user {user_id}")

    if is_recurring:
        logger.info(f"Creating next occurrence for recurring task {task_id}")
        # Add logic to create next task occurrence
        create_next_occurrence(task_id, user_id)


def handle_task_updated(data: dict):
    """Process task.updated event"""
    task_id = data['task_id']
    changes = data['changes']

    logger.info(f"Task updated: {task_id}, changes: {changes}")

    # Add your business logic here
    # Example: Update search index, notify collaborators, etc.


def handle_task_deleted(data: dict):
    """Process task.deleted event"""
    task_id = data['task_id']
    user_id = data['user_id']

    logger.info(f"Task deleted: {task_id} by user {user_id}")

    # Add your business logic here
    # Example: Clean up related data, update analytics, etc.


def create_next_occurrence(task_id: str, user_id: str):
    """Create next occurrence of recurring task"""
    # Placeholder for recurring task logic
    logger.info(f"Creating next occurrence for task {task_id}")

    # In production, this would:
    # 1. Fetch task recurrence rule
    # 2. Calculate next due date
    # 3. Create new task via API
    # 4. Publish task.created event


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
