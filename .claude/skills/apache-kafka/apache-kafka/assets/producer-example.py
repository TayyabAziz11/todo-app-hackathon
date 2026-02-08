"""
Kafka Producer Example using Dapr Pub/Sub
Publishes task lifecycle events to Kafka via Dapr
"""

import json
import uuid
from datetime import datetime, UTC
from dapr.clients import DaprClient


class TaskEventProducer:
    """Publishes task events to Kafka via Dapr"""

    def __init__(self, pubsub_name: str = "kafka-pubsub"):
        self.pubsub_name = pubsub_name

    def publish_task_created(self, user_id: str, task_id: str, title: str, due_date: str = None):
        """Publish task.created event"""
        event = self._create_event(
            event_type="com.todoapp.task.created",
            subject=f"task/{task_id}",
            data={
                "task_id": task_id,
                "user_id": user_id,
                "title": title,
                "due_date": due_date,
                "created_at": datetime.now(UTC).isoformat()
            }
        )
        self._publish(topic="task-events", event=event, partition_key=user_id)

    def publish_task_completed(self, user_id: str, task_id: str, is_recurring: bool = False):
        """Publish task.completed event"""
        event = self._create_event(
            event_type="com.todoapp.task.completed",
            subject=f"task/{task_id}",
            data={
                "task_id": task_id,
                "user_id": user_id,
                "is_recurring": is_recurring,
                "completed_at": datetime.now(UTC).isoformat()
            }
        )
        self._publish(topic="task-events", event=event, partition_key=user_id)

    def publish_task_updated(self, user_id: str, task_id: str, changes: dict):
        """Publish task.updated event"""
        event = self._create_event(
            event_type="com.todoapp.task.updated",
            subject=f"task/{task_id}",
            data={
                "task_id": task_id,
                "user_id": user_id,
                "changes": changes,
                "updated_at": datetime.now(UTC).isoformat()
            }
        )
        self._publish(topic="task-events", event=event, partition_key=user_id)

    def publish_task_deleted(self, user_id: str, task_id: str):
        """Publish task.deleted event"""
        event = self._create_event(
            event_type="com.todoapp.task.deleted",
            subject=f"task/{task_id}",
            data={
                "task_id": task_id,
                "user_id": user_id,
                "deleted_at": datetime.now(UTC).isoformat()
            }
        )
        self._publish(topic="task-events", event=event, partition_key=user_id)

    def _create_event(self, event_type: str, subject: str, data: dict) -> dict:
        """Create CloudEvents-compliant event"""
        return {
            "specversion": "1.0",
            "id": str(uuid.uuid4()),
            "source": "todo-backend",
            "type": event_type,
            "datacontenttype": "application/json",
            "time": datetime.now(UTC).isoformat(),
            "subject": subject,
            "data": data
        }

    def _publish(self, topic: str, event: dict, partition_key: str):
        """Publish event to Kafka via Dapr"""
        with DaprClient() as client:
            client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=topic,
                data=json.dumps(event["data"]),
                data_content_type="application/json",
                metadata={
                    "rawPayload": "true",
                    "partitionKey": partition_key  # Ensures ordering per user
                }
            )


# Usage example
if __name__ == "__main__":
    producer = TaskEventProducer()

    # Publish task created event
    producer.publish_task_created(
        user_id="user-123",
        task_id="task-456",
        title="Complete Kafka skill",
        due_date="2026-02-10T12:00:00Z"
    )

    print("Event published successfully")
