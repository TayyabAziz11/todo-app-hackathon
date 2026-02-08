# Dapr Hello World - Python

A simple Python service demonstrating Dapr building blocks.

## Prerequisites

- Python 3.8+
- Dapr CLI installed and initialized

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Dapr
dapr run --app-id hello-python --app-port 5000 --dapr-http-port 3500 -- python app.py
```

## Test Endpoints

**Service Invocation:**
```bash
curl http://localhost:5000/hello
curl -X POST http://localhost:5000/hello -H "Content-Type: application/json" -d '{"name": "Alice"}'
```

**State Management:**
```bash
# Save state
curl -X POST http://localhost:5000/state/save -H "Content-Type: application/json" \
  -d '{"key": "user-1", "value": {"name": "Alice", "age": 30}}'

# Get state
curl http://localhost:5000/state/get/user-1
```

**Pub/Sub:**
```bash
# Publish event
curl -X POST http://localhost:5000/publish -H "Content-Type: application/json" \
  -d '{"topic": "messages", "message": {"text": "Hello Dapr!"}}'
```

**Service-to-Service:**
```bash
# Invoke another service
curl -X POST http://localhost:5000/invoke/another-service/hello \
  -H "Content-Type: application/json" -d '{"name": "Bob"}'
```
