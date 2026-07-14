from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.models import User, Device, DeviceGroup
from app.schemas.schemas import DeviceGroupCreate, DeviceGroupResponse
from app.api.deps.auth import get_current_user

router = APIRouter()


@router.get("/departments")
async def list_departments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DeviceGroup.name).where(DeviceGroup.user_id == current_user.id)
    )
    return result.scalars().all()


@router.get("")
async def list_fleet(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Device).where(Device.user_id == current_user.id)
    )
    devices = result.scalars().all()
    fleet = []
    for device in devices:
        dept_name = None
        if device.group_id:
            grp = await db.execute(
                select(DeviceGroup.name).where(DeviceGroup.id == device.group_id)
            )
            dept_name = grp.scalar_one_or_none()
        fleet.append({
            "id": device.id,
            "name": device.name,
            "status": device.status,
            "os": device.os,
            "user": current_user.name or current_user.email,
            "department": dept_name or "Ungrouped",
            "ip_address": getattr(device, 'ip_address', None) or None,
            "last_seen": getattr(device, 'last_seen', None),
        })
    return fleet


@router.get("/groups", response_model=List[DeviceGroupResponse])
async def list_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DeviceGroup).where(DeviceGroup.user_id == current_user.id)
    )
    groups = result.scalars().all()

    response = []
    for group in groups:
        count_result = await db.execute(
            select(func.count(Device.id)).where(Device.group_id == group.id)
        )
        device_count = count_result.scalar() or 0
        response.append(DeviceGroupResponse(
            id=group.id,
            name=group.name,
            group_type=group.group_type,
            color=group.color,
            device_count=device_count,
        ))
    return response


@router.post("", response_model=DeviceGroupResponse)
async def create_group(
    data: DeviceGroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    group = DeviceGroup(
        user_id=current_user.id,
        name=data.name,
        group_type=data.group_type,
        color=data.color,
    )
    db.add(group)
    await db.flush()

    return DeviceGroupResponse(
        id=group.id,
        name=group.name,
        group_type=group.group_type,
        color=group.color,
        device_count=0,
    )


@router.delete("/{group_id}")
async def delete_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DeviceGroup).where(DeviceGroup.id == group_id, DeviceGroup.user_id == current_user.id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    await db.execute(
        Device.__table__.update()
        .where(Device.group_id == group_id)
        .values(group_id=None)
    )
    await db.delete(group)
    return {"message": "Group deleted"}
