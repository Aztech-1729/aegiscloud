"""Phase 6: Agent update endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import Device, AgentUpdate
from app.services.updates.service import update_service
from app.services.device_auth import authenticate_device

router = APIRouter()


@router.get("/check")
async def check_for_update(
    request: Request,
    db: AsyncSession = Depends(get_db),
    device: Device = Depends(authenticate_device),
):
    """Check if an update is available for this device.
    
    Phase 6: Returns update info with SHA256 and signature
    for client-side verification before applying.
    """
    result = await update_service.check_update_needed(db, device)
    return result


@router.post("/download/{version}")
async def record_download(
    version: str,
    db: AsyncSession = Depends(get_db),
    device: Device = Depends(authenticate_device),
):
    """Record that a device is downloading an update."""
    await update_service.record_download(db, version)
    return {"message": "Download recorded"}


@router.post("/install/{version}")
async def record_install(
    version: str,
    db: AsyncSession = Depends(get_db),
    device: Device = Depends(authenticate_device),
):
    """Record that a device has installed an update."""
    await update_service.record_install(db, device, version)
    return {"message": "Install recorded", "version": version}


@router.get("/latest")
async def get_latest_version(
    beta: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Get the latest available agent version (public endpoint)."""
    update = await update_service.get_latest_version(db, beta=beta)
    if not update:
        return {"version": None, "available": False}

    return {
        "version": update.version,
        "available": True,
        "release_notes": update.release_notes,
        "is_mandatory": update.is_mandatory,
        "is_beta": update.is_beta,
        "released_at": update.released_at.isoformat(),
    }
