"""Phase 9: Scheduler endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import User, Schedule, ScheduleType
from app.api.deps.auth import get_current_user
from app.services.scheduler.service import scheduler_service

router = APIRouter()


@router.get("")
async def list_schedules(
    device_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all schedules for the user."""
    query = select(Schedule).where(Schedule.user_id == current_user.id)
    if device_id:
        query = query.where(Schedule.device_id == device_id)
    query = query.order_by(Schedule.created_at.desc())

    result = await db.execute(query)
    schedules = result.scalars().all()

    return [
        {
            "id": s.id,
            "device_id": s.device_id,
            "name": s.name,
            "description": s.description,
            "schedule_type": s.schedule_type.value if hasattr(s.schedule_type, 'value') else s.schedule_type,
            "time_of_day": s.time_of_day,
            "day_of_week": s.day_of_week,
            "day_of_month": s.day_of_month,
            "commands": s.commands,
            "is_active": s.is_active,
            "last_run": s.last_run.isoformat() if s.last_run else None,
            "next_run": s.next_run.isoformat() if s.next_run else None,
        }
        for s in schedules
    ]


@router.post("")
async def create_schedule(
    name: str,
    device_id: str,
    schedule_type: str,
    commands: list,
    time_of_day: str = "02:00",
    day_of_week: Optional[int] = None,
    day_of_month: Optional[int] = None,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new scheduled maintenance task."""
    try:
        st = ScheduleType(schedule_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid schedule type: {schedule_type}")

    schedule = await scheduler_service.create_schedule(
        db=db,
        user_id=current_user.id,
        device_id=device_id,
        name=name,
        schedule_type=st,
        commands=commands,
        description=description,
        time_of_day=time_of_day,
        day_of_week=day_of_week,
        day_of_month=day_of_month,
    )

    return {
        "id": schedule.id,
        "name": schedule.name,
        "next_run": schedule.next_run.isoformat() if schedule.next_run else None,
    }


@router.patch("/{schedule_id}/toggle")
async def toggle_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Enable or disable a schedule."""
    result = await db.execute(
        select(Schedule).where(Schedule.id == schedule_id, Schedule.user_id == current_user.id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    schedule.is_active = not schedule.is_active
    return {"id": schedule.id, "is_active": schedule.is_active}


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a schedule."""
    result = await db.execute(
        select(Schedule).where(Schedule.id == schedule_id, Schedule.user_id == current_user.id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    await db.delete(schedule)
    return {"message": "Schedule deleted"}
