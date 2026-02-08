"""
User Service - Phase V.3
Microservice for user management and notification preferences
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from datetime import time
import logging
import httpx
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dapr configuration
DAPR_SIDECAR_URL = os.getenv("DAPR_HTTP_ENDPOINT", "http://localhost:3500")
STATE_STORE_NAME = "statestore"

# Pydantic models for notification preferences (T063)
class NotificationPreferences(BaseModel):
    """
    T063: Notification preferences data model
    Stored in Dapr State Store with key: user-prefs:{user_id}
    """
    user_id: str
    email_enabled: bool = Field(default=True, description="Enable/disable email notifications")
    email_address: Optional[str] = Field(default=None, description="User's email address")
    quiet_hours_start: Optional[str] = Field(default=None, description="Quiet hours start time (HH:MM format, e.g., '22:00')")
    quiet_hours_end: Optional[str] = Field(default=None, description="Quiet hours end time (HH:MM format, e.g., '08:00')")
    reminder_enabled: bool = Field(default=True, description="Enable/disable reminder notifications")
    completion_notifications: bool = Field(default=True, description="Notify on TODO completion")

class NotificationPreferencesUpdate(BaseModel):
    """Request model for updating notification preferences"""
    email_enabled: Optional[bool] = None
    email_address: Optional[str] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    reminder_enabled: Optional[bool] = None
    completion_notifications: Optional[bool] = None

app = FastAPI(
    title="User Service",
    description="Microservice for user management and notification preferences",
    version="2.0.0"  # Updated for Phase V.3
)

# Helper functions for Dapr State Store
async def save_preferences_to_state(user_id: str, prefs_data: dict):
    """Save notification preferences to Dapr State Store"""
    async with httpx.AsyncClient() as client:
        save_url = f"{DAPR_SIDECAR_URL}/v1.0/state/{STATE_STORE_NAME}"
        payload = [{"key": f"user-prefs:{user_id}", "value": prefs_data}]
        response = await client.post(save_url, json=payload)
        if response.status_code != 204:
            raise HTTPException(status_code=500, detail="Failed to save preferences to state store")

async def get_preferences_from_state(user_id: str) -> Optional[dict]:
    """Retrieve notification preferences from Dapr State Store"""
    async with httpx.AsyncClient() as client:
        get_url = f"{DAPR_SIDECAR_URL}/v1.0/state/{STATE_STORE_NAME}/user-prefs:{user_id}"
        response = await client.get(get_url)
        if response.status_code == 200:
            data = response.json()
            return data if data else None
        return None

@app.get("/health/ready")
async def readiness_probe():
    return JSONResponse(
        status_code=200,
        content={"status": "ready", "service": "user-service"}
    )

@app.get("/health/live")
async def liveness_probe():
    return JSONResponse(
        status_code=200,
        content={"status": "alive", "service": "user-service"}
    )

@app.get("/")
async def root():
    return {
        "service": "user-service",
        "version": "2.0.0",
        "status": "operational",
        "features": ["notification-preferences"]
    }

# T064: Notification Preferences API Endpoints
@app.get("/api/v1/users/{user_id}/notification-preferences", response_model=NotificationPreferences)
async def get_notification_preferences(user_id: str):
    """
    T064: GET notification preferences for a user

    Returns the user's notification preferences. If no preferences exist,
    returns default preferences.

    Args:
        user_id: User identifier

    Returns:
        NotificationPreferences object with current settings
    """
    prefs_data = await get_preferences_from_state(user_id)

    if not prefs_data:
        # Return default preferences
        default_prefs = NotificationPreferences(user_id=user_id)
        logger.info(f"No preferences found for user {user_id}, returning defaults")
        return default_prefs

    logger.info(f"Retrieved preferences for user {user_id}")
    return NotificationPreferences(**prefs_data)

@app.put("/api/v1/users/{user_id}/notification-preferences", response_model=NotificationPreferences)
async def update_notification_preferences(
    user_id: str,
    preferences_update: NotificationPreferencesUpdate
):
    """
    T064: PUT/Update notification preferences for a user

    Updates the user's notification preferences. Only provided fields are updated.

    Args:
        user_id: User identifier
        preferences_update: Fields to update (partial update supported)

    Returns:
        Updated NotificationPreferences object
    """
    # Get existing preferences or create defaults
    existing_prefs_data = await get_preferences_from_state(user_id)

    if existing_prefs_data:
        prefs = NotificationPreferences(**existing_prefs_data)
    else:
        prefs = NotificationPreferences(user_id=user_id)

    # Update only provided fields
    update_data = preferences_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prefs, field, value)

    # Validate quiet hours format if provided
    if prefs.quiet_hours_start:
        try:
            time.fromisoformat(prefs.quiet_hours_start)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="quiet_hours_start must be in HH:MM format (e.g., '22:00')"
            )

    if prefs.quiet_hours_end:
        try:
            time.fromisoformat(prefs.quiet_hours_end)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="quiet_hours_end must be in HH:MM format (e.g., '08:00')"
            )

    # Save to state store
    await save_preferences_to_state(user_id, prefs.model_dump())

    logger.info(f"Updated preferences for user {user_id}")
    return prefs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
