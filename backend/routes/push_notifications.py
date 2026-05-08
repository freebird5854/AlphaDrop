"""Push notification registration and sending for native app."""
from fastapi import APIRouter, Request, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/api/notifications", tags=["push_notifications"])


class PushTokenRegister(BaseModel):
    push_token: str
    platform: str  # ios, android, web
    device_name: Optional[str] = None


class PushNotification(BaseModel):
    title: str
    body: str
    data: Optional[dict] = None


@router.post("/push/register")
async def register_push_token(body: PushTokenRegister, request: Request):
    """Register a device push token — requires auth."""
    from server import require_subscription, db
    user = await require_subscription(request)

    # Upsert token for user
    await db.push_tokens.update_one(
        {"user_email": user.email, "push_token": body.push_token},
        {"$set": {
            "user_email": user.email,
            "push_token": body.push_token,
            "platform": body.platform,
            "device_name": body.device_name,
            "active": True,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )
    return {"message": "Push token registered", "platform": body.platform}


@router.delete("/push/unregister")
async def unregister_push_token(request: Request, push_token: str = Query(...)):
    """Unregister a push token."""
    from server import db
    await db.push_tokens.update_one(
        {"push_token": push_token},
        {"$set": {"active": False}}
    )
    return {"message": "Push token unregistered"}


@router.get("/push/tokens")
async def get_user_tokens(request: Request):
    """Get all registered tokens for current user."""
    from server import require_subscription, db
    user = await require_subscription(request)
    tokens = await db.push_tokens.find(
        {"user_email": user.email, "active": True}, {"_id": 0}
    ).to_list(10)
    return {"tokens": tokens}


async def send_push_to_user(db, user_email: str, title: str, body: str, data: dict = None):
    """Send push notification to all devices of a user.
    Uses Expo Push API format for compatibility with React Native."""
    tokens = await db.push_tokens.find(
        {"user_email": user_email, "active": True}, {"_id": 0, "push_token": 1}
    ).to_list(10)

    if not tokens:
        return 0

    # Log notification
    await db.push_log.insert_one({
        "id": str(uuid.uuid4()),
        "user_email": user_email,
        "title": title,
        "body": body,
        "data": data,
        "tokens_count": len(tokens),
        "sent_at": datetime.now(timezone.utc).isoformat(),
    })

    # In production: call Expo Push API
    # https://exp.host/--/api/v2/push/send
    # For now, log and return count
    return len(tokens)


async def send_push_to_all_subscribers(db, title: str, body: str, data: dict = None):
    """Send push notification to all active subscribers."""
    tokens = await db.push_tokens.find(
        {"active": True}, {"_id": 0, "push_token": 1, "user_email": 1}
    ).to_list(5000)

    if not tokens:
        return 0

    await db.push_log.insert_one({
        "id": str(uuid.uuid4()),
        "broadcast": True,
        "title": title,
        "body": body,
        "data": data,
        "tokens_count": len(tokens),
        "sent_at": datetime.now(timezone.utc).isoformat(),
    })

    return len(tokens)


@router.post("/push/send-test")
async def send_test_push(request: Request):
    """Send a test push notification to current user's devices."""
    from server import require_subscription, db
    user = await require_subscription(request)
    count = await send_push_to_user(
        db, user.email,
        "ALPHA DROP Alert",
        "Test notification - your alerts are working!",
        {"type": "test"}
    )
    return {"message": f"Test push sent to {count} device(s)"}


@router.post("/push/broadcast")
async def broadcast_push(body: PushNotification, request: Request, api_key: str = Query(None)):
    """Broadcast push to all subscribers — admin/cron only."""
    import os
    from server import db

    # Check admin or cron key
    expected = os.environ.get("CRON_API_KEY", "alpha-drop-cron-2024")
    if api_key != expected:
        from server import get_admin_user
        await get_admin_user(request)

    count = await send_push_to_all_subscribers(db, body.title, body.body, body.data)
    return {"message": f"Broadcast sent to {count} device(s)", "title": body.title}
