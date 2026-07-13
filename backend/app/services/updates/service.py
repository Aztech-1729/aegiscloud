"""Phase 6: Auto-Update Service.

Manages agent updates with:
- Signed releases (Ed25519 signatures)
- SHA256 verification
- Mandatory vs optional updates
- Beta channel support
- Download/install tracking
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import AgentUpdate, Device
from app.core.logging import get_logger

logger = get_logger(__name__)


class UpdateService:
    """Manages agent updates with signature verification."""

    async def get_latest_version(
        self,
        db: AsyncSession,
        current_version: Optional[str] = None,
        beta: bool = False,
    ) -> Optional[AgentUpdate]:
        """Get the latest available update."""
        query = select(AgentUpdate).order_by(AgentUpdate.released_at.desc())

        if not beta:
            query = query.where(AgentUpdate.is_beta == False)

        result = await db.execute(query.limit(1))
        return result.scalar_one_or_none()

    async def check_update_needed(
        self,
        db: AsyncSession,
        device: Device,
    ) -> dict:
        """Check if a device needs an update."""
        latest = await self.get_latest_version(db, device.agent_version)

        if not latest:
            return {"update_available": False}

        if device.agent_version == latest.version:
            return {"update_available": False}

        return {
            "update_available": True,
            "current_version": device.agent_version,
            "latest_version": latest.version,
            "is_mandatory": latest.is_mandatory,
            "release_notes": latest.release_notes,
            "download_url": latest.windows_x64_url,
            "sha256": latest.sha256_hash,
            "signature": latest.signature,
        }

    async def register_update(
        self,
        db: AsyncSession,
        version: str,
        windows_x64_url: str,
        sha256_hash: str,
        signature: str,
        release_notes: Optional[str] = None,
        windows_arm64_url: Optional[str] = None,
        is_mandatory: bool = False,
        is_beta: bool = False,
    ) -> AgentUpdate:
        """Register a new agent update release."""
        update = AgentUpdate(
            version=version,
            release_notes=release_notes,
            windows_x64_url=windows_x64_url,
            windows_arm64_url=windows_arm64_url,
            sha256_hash=sha256_hash,
            signature=signature,
            is_mandatory=is_mandatory,
            is_beta=is_beta,
        )
        db.add(update)
        await db.flush()
        logger.info("update_registered", version=version, mandatory=is_mandatory)
        return update

    async def record_download(self, db: AsyncSession, version: str) -> None:
        """Track download count for an update."""
        result = await db.execute(
            select(AgentUpdate).where(AgentUpdate.version == version)
        )
        update = result.scalar_one_or_none()
        if update:
            update.download_count = (update.download_count or 0) + 1
            await db.flush()

    async def record_install(self, db: AsyncSession, device: Device, version: str) -> None:
        """Record that a device has successfully installed an update."""
        device.agent_version = version
        device.pending_update_version = None

        result = await db.execute(
            select(AgentUpdate).where(AgentUpdate.version == version)
        )
        update = result.scalar_one_or_none()
        if update:
            update.install_count = (update.install_count or 0) + 1
            await db.flush()

        logger.info("update_installed", device_id=device.id, version=version)


update_service = UpdateService()
