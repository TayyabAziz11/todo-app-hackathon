"""
Notification Service - Phase V.3 T068
Microservice for reminders and email delivery via Dapr SMTP binding
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import httpx
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Notification Service",
    description="Microservice for notifications and reminders",
    version="2.0.0"
)

# Configuration
USER_SERVICE_URL = "http://user-service:8000"
DAPR_HTTP_PORT = 3500

# Pydantic models for event payloads
class ReminderDueEvent(BaseModel):
    todo_id: str
    title: str
    description: Optional[str]
    priority: str
    due_date: str
    user_id: str
    reminder_time: str

class TodoCompletedEvent(BaseModel):
    todo_id: str
    title: str
    user_id: str
    completed_at: str

class TodoDeletedEvent(BaseModel):
    todo_id: str
    title: str
    user_id: str
    deleted_at: str

# Helper function to get user notification preferences
async def get_user_preferences(user_id: str) -> Dict[str, Any]:
    """Fetch user notification preferences from user-service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{USER_SERVICE_URL}/api/v1/users/{user_id}/notification-preferences")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch preferences for user {user_id}: {e}")
        # Return defaults if user-service is unavailable
        return {
            "email_enabled": True,
            "email_address": None,
            "reminder_enabled": True,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00"
        }

# Helper function to check if current time is in quiet hours
def is_quiet_hours(start_time: str, end_time: str) -> bool:
    """Check if current time falls within quiet hours"""
    try:
        now = datetime.utcnow().time()
        start_h, start_m = map(int, start_time.split(':'))
        end_h, end_m = map(int, end_time.split(':'))

        from datetime import time
        start = time(start_h, start_m)
        end = time(end_h, end_m)

        # Handle overnight quiet hours
        if start <= end:
            return start <= now <= end
        else:
            return now >= start or now <= end
    except Exception as e:
        logger.warning(f"Failed to parse quiet hours: {e}")
        return False

# Helper function to send email via Dapr SMTP binding
async def send_email(to_email: str, subject: str, body: str):
    """Send email using Dapr SMTP binding"""
    try:
        binding_request = {
            "data": {
                "emailTo": to_email,
                "subject": subject,
                "body": body
            },
            "metadata": {},
            "operation": "create"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/bindings/smtp",
                json=binding_request,
                timeout=10.0
            )
            response.raise_for_status()
            logger.info(f"Email sent successfully to {to_email}")
            return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

# Event Handlers
@app.post("/events/reminder-due")
async def handle_reminder_due(request: Request):
    """
    T068: Handle todo.reminder.due events from Kafka
    Sends reminder emails to users about upcoming due dates
    """
    try:
        # Parse CloudEvents envelope
        cloud_event = await request.json()
        logger.info(f"Received reminder-due event: {cloud_event}")

        # Extract event data - handle nested CloudEvent structure
        event_data = cloud_event.get("data", {})
        if isinstance(event_data, str):
            event_data = json.loads(event_data)

        # Handle nested data.data structure from Dapr
        if "data" in event_data and isinstance(event_data["data"], dict):
            event_data = event_data["data"]

        event = ReminderDueEvent(**event_data)

        # Get user notification preferences
        prefs = await get_user_preferences(event.user_id)

        # Check if user has email notifications enabled
        if not prefs.get("email_enabled", True):
            logger.info(f"Email notifications disabled for user {event.user_id}")
            return {"status": "skipped", "reason": "email_disabled"}

        if not prefs.get("reminder_enabled", True):
            logger.info(f"Reminders disabled for user {event.user_id}")
            return {"status": "skipped", "reason": "reminders_disabled"}

        # Check quiet hours
        if is_quiet_hours(prefs.get("quiet_hours_start", "22:00"), prefs.get("quiet_hours_end", "08:00")):
            logger.info(f"Skipping reminder due to quiet hours for user {event.user_id}")
            return {"status": "skipped", "reason": "quiet_hours"}

        # Get email address
        email_address = prefs.get("email_address")
        if not email_address:
            logger.warning(f"No email address configured for user {event.user_id}")
            return {"status": "skipped", "reason": "no_email"}

        # Send reminder email
        subject = f"Reminder: {event.title} is due soon"
        body = f"""Hello {event.user_id},

This is a friendly reminder that your TODO item is due soon:

Title: {event.title}
Priority: {event.priority}
Due Date: {event.due_date}
{f'Description: {event.description}' if event.description else ''}

Please complete it at your earliest convenience.

Best regards,
Todo App Team
"""

        success = await send_email(email_address, subject, body)

        if success:
            return {"status": "success", "message": "Reminder email sent"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")

    except Exception as e:
        logger.error(f"Error handling reminder-due event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events/todo-completed")
async def handle_todo_completed(request: Request):
    """
    Handle todo.completed events
    Sends congratulations emails when users complete tasks
    """
    try:
        cloud_event = await request.json()
        logger.info(f"Received todo-completed event: {cloud_event}")

        event_data = cloud_event.get("data", {})
        if isinstance(event_data, str):
            event_data = json.loads(event_data)

        # Handle nested data.data structure
        if "data" in event_data and isinstance(event_data["data"], dict):
            event_data = event_data["data"]

        event = TodoCompletedEvent(**event_data)

        # Get user preferences
        prefs = await get_user_preferences(event.user_id)

        if not prefs.get("email_enabled", True):
            return {"status": "skipped", "reason": "email_disabled"}

        email_address = prefs.get("email_address")
        if not email_address:
            return {"status": "skipped", "reason": "no_email"}

        # Send completion notification
        subject = f"Task Completed: {event.title}"
        body = f"""Hello {event.user_id},

Great job! You've completed the following task:

Title: {event.title}
Completed At: {event.completed_at}

Keep up the excellent work!

Best regards,
Todo App Team
"""

        await send_email(email_address, subject, body)
        return {"status": "success", "message": "Completion notification sent"}

    except Exception as e:
        logger.error(f"Error handling todo-completed event: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/events/todo-deleted")
async def handle_todo_deleted(request: Request):
    """
    T071: Handle todo.deleted events
    Could be used to cancel pending reminders or log deletions
    """
    try:
        cloud_event = await request.json()
        logger.info(f"Received todo-deleted event: {cloud_event}")

        event_data = cloud_event.get("data", {})
        if isinstance(event_data, str):
            event_data = json.loads(event_data)

        # Handle nested data.data structure
        if "data" in event_data and isinstance(event_data["data"], dict):
            event_data = event_data["data"]

        event = TodoDeletedEvent(**event_data)

        # For now, just log the deletion
        # In a more advanced implementation, we would:
        # - Cancel any pending scheduled reminders
        # - Remove from notification queue
        logger.info(f"TODO {event.todo_id} deleted by user {event.user_id}. Pending reminders would be cancelled here.")

        return {"status": "success", "message": "Deletion processed"}

    except Exception as e:
        logger.error(f"Error handling todo-deleted event: {e}")
        return {"status": "error", "message": str(e)}

# T074: DLQ Consumer - Poison Message Handler
@app.post("/events/dlq")
async def handle_dlq_message(request: Request):
    """
    Handle poison messages from DLQ topic
    Log failed events without reprocessing to avoid loops
    """
    try:
        cloud_event = await request.json()

        # Extract CloudEvent metadata
        event_id = cloud_event.get("id", "unknown")
        event_type = cloud_event.get("type", "unknown")
        event_source = cloud_event.get("source", "unknown")

        # Extract failure reason from data or metadata
        event_data = cloud_event.get("data", {})
        if isinstance(event_data, str):
            event_data = json.loads(event_data)

        # Log the poison message
        logger.error(
            f"DLQ Message Received - "
            f"ID: {event_id}, "
            f"Type: {event_type}, "
            f"Source: {event_source}, "
            f"Timestamp: {datetime.utcnow().isoformat()}Z, "
            f"Data: {json.dumps(event_data)}"
        )

        # Store in a persistent log or monitoring system
        # For now, just acknowledge receipt without reprocessing
        return {
            "status": "logged",
            "message": "Poison message logged, no reprocessing",
            "event_id": event_id
        }

    except Exception as e:
        logger.error(f"Error handling DLQ message: {e}")
        # Even DLQ handler errors should not retry
        return {"status": "error", "message": str(e)}

# Health endpoints
@app.get("/health/ready")
async def readiness_probe():
    return JSONResponse(
        status_code=200,
        content={"status": "ready", "service": "notification-service"}
    )

@app.get("/health/live")
async def liveness_probe():
    return JSONResponse(
        status_code=200,
        content={"status": "alive", "service": "notification-service"}
    )

@app.get("/")
async def root():
    return {
        "service": "notification-service",
        "version": "2.0.0",
        "status": "operational",
        "features": ["email_reminders", "completion_notifications", "deletion_handling"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
