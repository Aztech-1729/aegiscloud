"""Events API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.events.stream import event_stream
from app.api.deps.auth import get_current_user
from app.models.models import User

router = APIRouter()


@router.get("")
async def get_recent_events(
    limit: int = 100,
    event_type: str = None,
    severity: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get recent events for the user."""
    events = await event_stream.get_recent_events(
        db=db,
        user_id=current_user.id,
        limit=limit,
        event_type=event_type,
        severity=severity,
    )
    return {"events": events, "total": len(events)}


@router.get("/stream")
async def stream_events(
    current_user: User = Depends(get_current_user),
):
    """Get WebSocket endpoint for real-time event streaming.
    
    Note: Actual WebSocket implementation would be in the WebSocket router.
    This endpoint is for documentation purposes.
    """
    return {
        "websocket_url": f"/ws/events?token=<access_token>",
        "description": "Connect via WebSocket for real-time event streaming",
    }
