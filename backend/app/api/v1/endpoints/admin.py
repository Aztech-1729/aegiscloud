from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.models import User, Device, Task, Subscription
from app.schemas.schemas import AdminUserResponse
from app.api.deps.auth import get_admin_user

router = APIRouter()


@router.get("/users", response_model=List[AdminUserResponse])
async def list_users(
    page: int = 1,
    per_page: int = 20,
    admin: object = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * per_page
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(offset).limit(per_page)
    )
    return result.scalars().all()


@router.get("/stats")
async def admin_stats(
    admin: object = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    user_count = await db.execute(select(func.count(User.id)))
    device_count = await db.execute(select(func.count(Device.id)))
    task_count = await db.execute(select(func.count(Task.id)))
    active_subscriptions = await db.execute(
        select(func.count(Subscription.id)).where(Subscription.status == "active")
    )

    return {
        "total_users": user_count.scalar() or 0,
        "total_devices": device_count.scalar() or 0,
        "total_tasks": task_count.scalar() or 0,
        "active_subscriptions": active_subscriptions.scalar() or 0,
    }


@router.put("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: str,
    admin: object = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    return {"id": user.id, "is_active": user.is_active}


@router.get("/devices")
async def admin_devices(
    page: int = 1,
    per_page: int = 50,
    admin: object = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * per_page
    result = await db.execute(
        select(Device).order_by(Device.created_at.desc()).offset(offset).limit(per_page)
    )
    return result.scalars().all()


@router.get("/tasks")
async def admin_tasks(
    page: int = 1,
    per_page: int = 50,
    admin: object = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * per_page
    result = await db.execute(
        select(Task).order_by(Task.created_at.desc()).offset(offset).limit(per_page)
    )
    return result.scalars().all()
