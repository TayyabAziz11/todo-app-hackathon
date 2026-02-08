"""
Dapr Hello World - Python Service
Demonstrates: Service invocation, state management, pub/sub
"""

from flask import Flask, request, jsonify
from dapr.clients import DaprClient
from cloudevents.http import from_http
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DAPR_STATE_STORE = "statestore"
DAPR_PUBSUB = "pubsub"


@app.route('/hello', methods=['GET', 'POST'])
def hello():
    """Basic service invocation endpoint"""
    data = request.json if request.method == 'POST' else {}
    name = data.get('name', 'World')
    return jsonify({'message': f'Hello, {name}!'})


@app.route('/state/save', methods=['POST'])
def save_state():
    """Save data to Dapr state store"""
    data = request.json
    key = data.get('key')
    value = data.get('value')

    with DaprClient() as client:
        client.save_state(DAPR_STATE_STORE, key, json.dumps(value))

    logger.info(f"Saved state: {key}")
    return jsonify({'status': 'saved', 'key': key})


@app.route('/state/get/<key>', methods=['GET'])
def get_state(key):
    """Retrieve data from Dapr state store"""
    with DaprClient() as client:
        state = client.get_state(DAPR_STATE_STORE, key)

    if state.data:
        value = json.loads(state.data)
        logger.info(f"Retrieved state: {key}")
        return jsonify({'key': key, 'value': value})
    else:
        return jsonify({'error': 'Key not found'}), 404


@app.route('/publish', methods=['POST'])
def publish_event():
    """Publish event to Dapr pub/sub"""
    data = request.json
    topic = data.get('topic', 'messages')
    message = data.get('message')

    with DaprClient() as client:
        client.publish_event(
            pubsub_name=DAPR_PUBSUB,
            topic_name=topic,
            data=json.dumps(message),
            data_content_type='application/json'
        )

    logger.info(f"Published event to topic: {topic}")
    return jsonify({'status': 'published', 'topic': topic})


@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    """Dapr subscription endpoint"""
    subscriptions = [{
        'pubsubname': DAPR_PUBSUB,
        'topic': 'messages',
        'route': '/messages'
    }]
    return jsonify(subscriptions)


@app.route('/messages', methods=['POST'])
def messages_subscriber():
    """Handle incoming pub/sub messages"""
    event = from_http(request.headers, request.get_data())
    data = json.loads(event.data)
    logger.info(f"Received message: {data}")
    return jsonify({'success': True}), 200


@app.route('/invoke/<service>/<method>', methods=['POST'])
def invoke_service(service, method):
    """Invoke another Dapr service"""
    data = request.json

    with DaprClient() as client:
        resp = client.invoke_method(
            app_id=service,
            method_name=method,
            data=json.dumps(data),
            http_verb='POST'
        )

    logger.info(f"Invoked {service}/{method}")
    return jsonify({'response': resp.text()})


if __name__ == '__main__':
    app.run(port=5000)
