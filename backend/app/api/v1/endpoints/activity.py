from sqlalchemy import select
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.models import User, Event
from app.api.deps.auth import get_current_user

router = APIRouter()


@router.get("")
async def get_activity(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Event)
        .where(Event.user_id == current_user.id)
        .order_by(Event.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    events = result.scalars().all()

    return [
        {
            "action": event.event_type,
            "device": event.device_id,
            "time": event.created_at.isoformat(),
            "status": event.severity,
        }
        for event in events
    ]
