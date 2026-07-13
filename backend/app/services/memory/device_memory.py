"""AI Memory System — Persistent device memory for contextual AI.

Instead of every conversation starting from scratch, the AI remembers:
- Previous scans and results
- Installed applications
- Known issues and patterns
- User preferences
- Historical performance data

This makes the AI progressively more useful on each device.

Memory Architecture:
    Device Memory
    ├── System Profile (hardware, OS, installed apps)
    ├── Performance History (CPU/RAM/GPU trends)
    ├── Issue History (past problems and solutions)
    ├── User Preferences (common tasks, settings)
    └── Recommendations (based on patterns)
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, Any
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import Device, DeviceMemory
from app.core.logging import get_logger

logger = get_logger(__name__)


class DeviceMemoryStore:
    """Manages persistent memory for each device."""

    async def get_memory(
        self,
        db: AsyncSession,
        device_id: str,
    ) -> dict:
        """Get the full memory for a device."""
        result = await db.execute(
            select(DeviceMemory).where(DeviceMemory.device_id == device_id)
        )
        memory = result.scalar_one_or_none()

        if not memory:
            return self._empty_memory()

        return {
            "device_id": device_id,
            "system_profile": memory.system_profile or {},
            "performance_history": memory.performance_history or [],
            "issue_history": memory.issue_history or [],
            "installed_apps": memory.installed_apps or [],
            "user_preferences": memory.preferences or {},
            "recommendations": memory.recommendations or [],
            "last_updated": memory.updated_at.isoformat() if memory.updated_at else None,
            "memory_version": memory.memory_version,
        }

    async def update_system_profile(
        self,
        db: AsyncSession,
        device_id: str,
        profile: dict,
    ) -> None:
        """Update the device's system profile."""
        memory = await self._get_or_create(db, device_id)
        memory.system_profile = {**(memory.system_profile or {}), **profile}
        memory.updated_at = datetime.now(timezone.utc)
        await db.flush()

    async def record_performance(
        self,
        db: AsyncSession,
        device_id: str,
        cpu: float,
        ram: float,
        gpu: Optional[float] = None,
        disk: Optional[float] = None,
        temp: Optional[float] = None,
    ) -> None:
        """Record a performance data point."""
        memory = await self._get_or_create(db, device_id)
        history = memory.performance_history or []

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu": cpu,
            "ram": ram,
            "gpu": gpu,
            "disk": disk,
            "temp": temp,
        }
        history.append(entry)

        # Keep last 1000 data points
        if len(history) > 1000:
            history = history[-1000:]

        memory.performance_history = history
        memory.updated_at = datetime.now(timezone.utc)
        await db.flush()

    async def record_issue(
        self,
        db: AsyncSession,
        device_id: str,
        issue: str,
        resolution: Optional[str] = None,
        severity: str = "medium",
    ) -> None:
        """Record a detected issue and its resolution."""
        memory = await self._get_or_create(db, device_id)
        issues = memory.issue_history or []

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "issue": issue,
            "resolution": resolution,
            "severity": severity,
            "resolved": resolution is not None,
        }
        issues.append(entry)

        # Keep last 200 issues
        if len(issues) > 200:
            issues = issues[-200:]

        memory.issue_history = issues
        memory.updated_at = datetime.now(timezone.utc)
        await db.flush()

    async def update_installed_apps(
        self,
        db: AsyncSession,
        device_id: str,
        apps: list[dict],
    ) -> None:
        """Update the list of installed applications."""
        memory = await self._get_or_create(db, device_id)
        memory.installed_apps = apps
        memory.updated_at = datetime.now(timezone.utc)
        await db.flush()

    async def update_preferences(
        self,
        db: AsyncSession,
        device_id: str,
        preferences: dict,
    ) -> None:
        """Update user preferences for this device."""
        memory = await self._get_or_create(db, device_id)
        memory.preferences = {**(memory.preferences or {}), **preferences}
        memory.updated_at = datetime.now(timezone.utc)
        await db.flush()

    async def generate_recommendations(
        self,
        db: AsyncSession,
        device_id: str,
    ) -> list[dict]:
        """Generate smart recommendations based on device memory."""
        memory_data = await self.get_memory(db, device_id)

        recommendations = []

        # Check performance history for patterns
        perf_history = memory_data.get("performance_history", [])
        if perf_history:
            recent = perf_history[-10:]  # Last 10 readings
            avg_cpu = sum(p.get("cpu", 0) for p in recent) / len(recent)
            avg_ram = sum(p.get("ram", 0) for p in recent) / len(recent)

            if avg_cpu > 80:
                recommendations.append({
                    "type": "performance",
                    "severity": "high",
                    "title": "High CPU usage detected",
                    "description": f"Average CPU usage is {avg_cpu:.0f}% over recent checks.",
                    "suggested_action": "Run process analysis to identify heavy processes",
                    "suggested_tool": "list_processes",
                })

            if avg_ram > 85:
                recommendations.append({
                    "type": "performance",
                    "severity": "high",
                    "title": "Memory pressure detected",
                    "description": f"Average RAM usage is {avg_ram:.0f}% — consider closing unused apps.",
                    "suggested_action": "Check startup applications",
                    "suggested_tool": "list_startup",
                })

        # Check for unresolved issues
        issues = memory_data.get("issue_history", [])
        unresolved = [i for i in issues if not i.get("resolved")]
        if unresolved:
            recommendations.append({
                "type": "issue",
                "severity": "medium",
                "title": f"{len(unresolved)} unresolved issue(s)",
                "description": "Previous issues haven't been fully resolved.",
                "suggested_action": "Review issue history",
            })

        # Check disk usage
        profile = memory_data.get("system_profile", {})
        if profile.get("disk_percent", 0) > 85:
            recommendations.append({
                "type": "maintenance",
                "severity": "medium",
                "title": "Disk space running low",
                "description": f"Disk usage at {profile['disk_percent']}%",
                "suggested_action": "Run storage analysis",
                "suggested_tool": "storage_analysis",
            })

        # Check if temp cleanup hasn't been done recently
        last_cleanup = None
        for issue in issues:
            if "clean" in issue.get("issue", "").lower():
                last_cleanup = issue.get("timestamp")

        if not last_cleanup or (
            datetime.fromisoformat(last_cleanup.replace("Z", "+00:00"))
            < datetime.now(timezone.utc) - timedelta(days=14)
        ):
            recommendations.append({
                "type": "maintenance",
                "severity": "low",
                "title": "Maintenance overdue",
                "description": "Temporary files haven't been cleaned in over 2 weeks.",
                "suggested_action": "Run cleanup",
                "suggested_tool": "clean_temp",
            })

        # Store recommendations
        memory = await self._get_or_create(db, device_id)
        memory.recommendations = recommendations
        await db.flush()

        return recommendations

    async def get_ai_context(
        self,
        db: AsyncSession,
        device_id: str,
    ) -> str:
        """Build a context string for the AI assistant.
        
        This gives the AI knowledge about the device's history
        so it can provide better, more contextual responses.
        """
        memory_data = await self.get_memory(db, device_id)

        context_parts = []

        # System profile
        profile = memory_data.get("system_profile", {})
        if profile:
            context_parts.append(f"Device Profile: {profile.get('os_name', 'Unknown')} on {profile.get('cpu_info', 'Unknown CPU')}, {profile.get('ram_total_gb', '?')} GB RAM")

        # Recent issues
        issues = memory_data.get("issue_history", [])
        recent_issues = issues[-5:] if issues else []
        if recent_issues:
            issue_names = [i["issue"] for i in recent_issues]
            context_parts.append(f"Recent Issues: {', '.join(issue_names)}")

        # Performance trends
        perf = memory_data.get("performance_history", [])
        if perf:
            recent = perf[-5:]
            avg_cpu = sum(p.get("cpu", 0) for p in recent) / len(recent)
            avg_ram = sum(p.get("ram", 0) for p in recent) / len(recent)
            context_parts.append(f"Recent Performance: CPU avg {avg_cpu:.0f}%, RAM avg {avg_ram:.0f}%")

        # Recommendations
        recs = memory_data.get("recommendations", [])
        if recs:
            rec_titles = [r["title"] for r in recs[:3]]
            context_parts.append(f"Active Recommendations: {', '.join(rec_titles)}")

        return " | ".join(context_parts) if context_parts else "No prior memory for this device."

    async def _get_or_create(
        self,
        db: AsyncSession,
        device_id: str,
    ) -> DeviceMemory:
        """Get or create device memory record."""
        result = await db.execute(
            select(DeviceMemory).where(DeviceMemory.device_id == device_id)
        )
        memory = result.scalar_one_or_none()

        if not memory:
            memory = DeviceMemory(device_id=device_id)
            db.add(memory)
            await db.flush()

        return memory

    def _empty_memory(self) -> dict:
        return {
            "device_id": None,
            "system_profile": {},
            "performance_history": [],
            "issue_history": [],
            "installed_apps": [],
            "user_preferences": {},
            "recommendations": [],
            "last_updated": None,
            "memory_version": 1,
        }


# Global memory store
device_memory = DeviceMemoryStore()
