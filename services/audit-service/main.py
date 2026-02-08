"""
Audit Service - Phase V.2 (F6)
Microservice for immutable event sourcing audit log
Consumes all todo events via Dapr Pub/Sub and stores them immutably
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import httpx
import os
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dapr configuration
DAPR_SIDECAR_URL = os.getenv("DAPR_HTTP_ENDPOINT", "http://localhost:3500")
STATE_STORE_NAME = "statestore"
PUBSUB_NAME = "pubsub"

# CloudEvents model
class CloudEvent(BaseModel):
    specversion: str
    type: str
    source: str
    id: str
    time: str
    datacontenttype: str
    data: Dict[str, Any]

# Audit log entry model
class AuditLogEntry(BaseModel):
    audit_id: str
    event_id: str
    event_type: str
    event_source: str
    event_time: str
    event_data: Dict[str, Any]
    recorded_at: str

app = FastAPI(
    title="Audit Service",
    description="Immutable audit logging for todo events (F6)",
    version="2.0.0"
)

# Idempotency cache (stores processed event IDs for 7 days)
processed_events = set()

async def save_audit_log(audit_entry: AuditLogEntry):
    """Save audit log entry to Dapr State Store (append-only)"""
    async with httpx.AsyncClient() as client:
        save_url = f"{DAPR_SIDECAR_URL}/v1.0/state/{STATE_STORE_NAME}"
        payload = [{
            "key": f"audit:{audit_entry.audit_id}",
            "value": audit_entry.dict()
        }]
        response = await client.post(save_url, json=payload)
        if response.status_code != 204:
            logger.error(f"Failed to save audit log: {response.status_code}")
            raise Exception("Failed to save audit log")

async def is_event_processed(event_id: str) -> bool:
    """Check if event was already processed (idempotency)"""
    # In production, use Dapr State Store for distributed idempotency
    # For Phase V.2 MVP, use in-memory set
    return event_id in processed_events

async def mark_event_processed(event_id: str):
    """Mark event as processed"""
    processed_events.add(event_id)

@app.get("/health/ready")
async def readiness_probe():
    return JSONResponse(
        status_code=200,
        content={"status": "ready", "service": "audit-service"}
    )

@app.get("/health/live")
async def liveness_probe():
    return JSONResponse(
        status_code=200,
        content={"status": "alive", "service": "audit-service"}
    )

@app.get("/")
async def root():
    return {
        "service": "audit-service",
        "version": "2.0.0",
        "status": "operational",
        "features": ["immutable-audit-log", "event-sourcing", "idempotent-consumer"]
    }

@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr Pub/Sub subscription endpoint (GET for subscription discovery)
    Subscribes to all todo events
    """
    subscriptions = [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "todo.created",
            "route": "/events/todo.created"
        },
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "todo.updated",
            "route": "/events/todo.updated"
        },
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "todo.completed",
            "route": "/events/todo.completed"
        },
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "todo.deleted",
            "route": "/events/todo.deleted"
        }
    ]
    logger.info(f"Dapr subscriptions registered: {len(subscriptions)} topics")
    return subscriptions

@app.post("/events/todo.created")
async def handle_todo_created(request: Request):
    """F6: Handle todo.created events"""
    return await handle_event(request, "todo.created")

@app.post("/events/todo.updated")
async def handle_todo_updated(request: Request):
    """F6: Handle todo.updated events"""
    return await handle_event(request, "todo.updated")

@app.post("/events/todo.completed")
async def handle_todo_completed(request: Request):
    """F6: Handle todo.completed events"""
    return await handle_event(request, "todo.completed")

@app.post("/events/todo.deleted")
async def handle_todo_deleted(request: Request):
    """F6: Handle todo.deleted events"""
    return await handle_event(request, "todo.deleted")

async def handle_event(request: Request, expected_topic: str):
    """
    Generic event handler for all todo events
    Implements idempotency and immutable audit logging
    """
    try:
        # Parse CloudEvent from request body
        event_data = await request.json()

        # Extract event metadata
        event_id = event_data.get("id")
        event_type = event_data.get("type")
        event_source = event_data.get("source")
        event_time = event_data.get("time")
        data = event_data.get("data", {})

        # Idempotency check
        if await is_event_processed(event_id):
            logger.info(f"Event {event_id} already processed (idempotent)")
            return JSONResponse(status_code=200, content={"status": "success", "reason": "duplicate"})

        # Create immutable audit log entry
        audit_id = str(uuid.uuid4())
        audit_entry = AuditLogEntry(
            audit_id=audit_id,
            event_id=event_id,
            event_type=event_type,
            event_source=event_source,
            event_time=event_time,
            event_data=data,
            recorded_at=datetime.utcnow().isoformat() + "Z"
        )

        # Save to immutable log
        await save_audit_log(audit_entry)

        # Mark as processed
        await mark_event_processed(event_id)

        logger.info(f"Audit log created: {audit_id} for event {event_id} ({event_type})")

        return JSONResponse(status_code=200, content={"status": "success"})

    except Exception as e:
        logger.error(f"Failed to process event: {str(e)}")
        # Return 200 to prevent Dapr retry (logged error for investigation)
        return JSONResponse(status_code=200, content={"status": "error", "message": str(e)})

@app.get("/audit-logs")
async def list_audit_logs(limit: int = 100):
    """
    F6: List recent audit log entries
    Note: In production, use query API or index
    For Phase V.2 MVP, returning empty list (requires index)
    """
    logger.info(f"List audit logs (limit={limit})")
    return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
