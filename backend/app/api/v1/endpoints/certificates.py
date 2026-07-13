"""Certificates API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.certificates.ca import cert_manager, ca
from app.api.deps.auth import get_current_user
from app.models.models import User

router = APIRouter()


@router.post("/enroll/{device_id}")
async def enroll_device(
    device_id: str,
    csr_pem: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Enroll a device with a certificate."""
    try:
        cert_pem = await cert_manager.enroll_device(
            db=db,
            device_id=device_id,
            csr_pem=csr_pem,
        )
        return {"certificate": cert_pem, "message": "Device enrolled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/renew/{device_id}")
async def renew_certificate(
    device_id: str,
    new_csr_pem: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Renew a device certificate."""
    try:
        cert_pem = await cert_manager.renew_certificate(
            db=db,
            device_id=device_id,
            new_csr_pem=new_csr_pem,
        )
        return {"certificate": cert_pem, "message": "Certificate renewed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{device_id}")
async def get_device_certificate(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the active certificate for a device."""
    cert = await cert_manager.get_device_cert(db=db, device_id=device_id)
    if not cert:
        raise HTTPException(status_code=404, detail="No active certificate found")
    return {"certificate": cert}


@router.get("/ca/certificate")
async def get_ca_certificate(current_user: User = Depends(get_current_user)):
    """Get the CA certificate (for verifying device certs)."""
    await ca.load_ca()
    return {"ca_certificate": ca.ca_cert or "CA not loaded"}


@router.get("/ca/crl")
async def get_crl(current_user: User = Depends(get_current_user)):
    """Get the Certificate Revocation List."""
    crl = await ca.get_crl()
    return {"crl": crl}
