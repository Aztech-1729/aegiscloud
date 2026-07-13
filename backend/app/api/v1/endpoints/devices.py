from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import secrets

from app.db.session import get_db
from app.models.models import User, Device, DeviceStatus, PairCode
from app.schemas.schemas import DeviceCreate, DevicePair, DeviceUpdate, DeviceResponse
from app.api.deps.auth import get_current_user
from app.core.config import settings
from app.core.security import create_pair_code

router = APIRouter()


@router.get("", response_model=List[DeviceResponse])
async def list_devices(
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Device).where(Device.user_id == current_user.id)
    if status:
        query = query.where(Device.status == status)
    query = query.order_by(Device.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.post("/pair", response_model=DeviceResponse)
async def pair_device(
    data: DevicePair,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PairCode).where(
            PairCode.code == data.pair_code,
            PairCode.used == False,
            PairCode.expires_at > datetime.now(timezone.utc),
        )
    )
    pair_code = result.scalar_one_or_none()
    if not pair_code:
        raise HTTPException(status_code=400, detail="Invalid or expired pair code")

    device_count = await db.execute(
        select(func.count(Device.id)).where(Device.user_id == current_user.id)
    )
    count = device_count.scalar()

    max_devices = {
        "free": settings.MAX_DEVICES_FREE,
        "pro": settings.MAX_DEVICES_PRO,
        "business": settings.MAX_DEVICES_BUSINESS,
        "enterprise": 999999,
    }
    if count >= max_devices.get(current_user.plan.value, 2):
        raise HTTPException(status_code=400, detail="Device limit reached for your plan")

    device = Device(
        user_id=current_user.id,
        name=f"Device-{secrets.token_hex(3).upper()}",
        status=DeviceStatus.offline,
        device_token=secrets.token_urlsafe(64),
    )
    db.add(device)

    pair_code.used = True

    await db.flush()
    return device


@router.post("/pair-code")
async def generate_pair_code(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    code = create_pair_code()
    pair_code = PairCode(
        user_id=current_user.id,
        code=code,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.PAIR_CODE_EXPIRY_MINUTES),
    )
    db.add(pair_code)
    await db.flush()

    return {
        "code": code,
        "expires_at": pair_code.expires_at.isoformat(),
    }


@router.patch("/{device_id}", response_model=DeviceResponse)
async def rename_device(
    device_id: str,
    data: DeviceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if data.name:
        device.name = data.name
    return device


@router.delete("/{device_id}")
async def remove_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    await db.delete(device)
    return {"message": "Device removed successfully"}


@router.post("/{device_id}/restart")
async def restart_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.status != DeviceStatus.online:
        raise HTTPException(status_code=400, detail="Device is not online")

    return {"message": "Restart command sent", "device_id": device_id}


@router.post("/{device_id}/shutdown")
async def shutdown_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.status != DeviceStatus.online:
        raise HTTPException(status_code=400, detail="Device is not online")

    return {"message": "Shutdown command sent", "device_id": device_id}


@router.post("/{device_id}/wake")
async def wake_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return {"message": "Wake-on-LAN signal sent", "device_id": device_id}
