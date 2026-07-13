"""Fleet Policy Groups — Apply policies to groups of devices.

Instead of managing each device individually:
    All Gaming PCs → Run Gaming Optimization → Every Friday at 2 AM
    All Work Laptops → Run Security Audit → Daily at 8 AM
    All Servers → Run DISM + SFC → Monthly

This is the enterprise value proposition:
    - Apply skills to device groups
    - Schedule group operations
    - Monitor group health
    - Bulk operations
"""
from typing import Optional
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import Device, DeviceGroup
from app.core.logging import get_logger

logger = get_logger(__name__)


class GroupPolicyType(str, Enum):
    """Types of group policies."""
    SCHEDULED_SKILL = "scheduled_skill"
    SCHEDULED_COMMAND = "scheduled_command"
    THRESHOLD_ALERT = "threshold_alert"
    AUTO_REMEDIATION = "auto_remediation"
    COMPLIANCE_CHECK = "compliance_check"


@dataclass
class FleetPolicy:
    """A policy applied to a group of devices."""
    id: str
    name: str
    description: str
    group_id: str
    group_name: str
    policy_type: GroupPolicyType
    
    # What to do
    skill_id: Optional[str] = None  # For scheduled_skill
    tool_name: Optional[str] = None  # For scheduled_command
    parameters: dict = field(default_factory=dict)
    
    # When to do it
    schedule_cron: Optional[str] = None  # e.g., "0 2 * * 5" (Friday 2 AM)
    schedule_type: Optional[str] = None  # "daily", "weekly", "monthly"
    
    # Conditions
    conditions: dict = field(default_factory=dict)  # e.g., {"cpu": "> 80%"}
    
    # Status
    is_active: bool = True
    last_executed: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    execution_count: int = 0
    
    # Metadata
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ============= BUILT-IN FLEET POLICY TEMPLATES =============

FLEET_POLICY_TEMPLATES = [
    {
        "id": "gaming-group-optimization",
        "name": "Gaming PCs — Weekly Optimization",
        "description": "Run Gaming Optimization skill on all gaming PCs every Friday at 2 AM",
        "group_filter": {"tags": ["gaming"]},
        "policy_type": GroupPolicyType.SCHEDULED_SKILL,
        "skill_id": "gaming-optimization",
        "schedule_cron": "0 2 * * 5",
        "schedule_type": "weekly",
    },
    {
        "id": "work-security-audit",
        "name": "Work PCs — Daily Security Audit",
        "description": "Run Security Audit on all work devices every day at 8 AM",
        "group_filter": {"tags": ["work"]},
        "policy_type": GroupPolicyType.SCHEDULED_SKILL,
        "skill_id": "security-audit",
        "schedule_cron": "0 8 * * *",
        "schedule_type": "daily",
    },
    {
        "id": "server-maintenance",
        "name": "Servers — Monthly Maintenance",
        "description": "Run Windows Repair on all servers on the 1st of each month at 3 AM",
        "group_filter": {"tags": ["server"]},
        "policy_type": GroupPolicyType.SCHEDULED_SKILL,
        "skill_id": "windows-repair",
        "schedule_cron": "0 3 1 * *",
        "schedule_type": "monthly",
    },
    {
        "id": "all-devices-cleanup",
        "name": "All Devices — Weekly Cleanup",
        "description": "Run Deep Cleanup on all devices every Sunday at midnight",
        "group_filter": {"all": True},
        "policy_type": GroupPolicyType.SCHEDULED_SKILL,
        "skill_id": "deep-cleanup",
        "schedule_cron": "0 0 * * 0",
        "schedule_type": "weekly",
    },
    {
        "id": "high-cpu-alert-all",
        "name": "All Devices — High CPU Alert",
        "description": "Alert admin when any device has CPU > 90% for 5 minutes",
        "group_filter": {"all": True},
        "policy_type": GroupPolicyType.THRESHOLD_ALERT,
        "conditions": {"metric": "cpu_usage", "operator": ">", "value": 90, "duration_minutes": 5},
    },
    {
        "id": "low-disk-auto-cleanup",
        "name": "All Devices — Auto Disk Cleanup",
        "description": "Automatically clean temp files when disk > 95%",
        "group_filter": {"all": True},
        "policy_type": GroupPolicyType.AUTO_REMEDIATION,
        "conditions": {"metric": "disk_percent", "operator": ">", "value": 95},
        "tool_name": "clean_temp",
        "parameters": {},
    },
    {
        "id": "defender-compliance",
        "name": "All Devices — Defender Compliance",
        "description": "Alert when Windows Defender is disabled on any device",
        "group_filter": {"all": True},
        "policy_type": GroupPolicyType.COMPLIANCE_CHECK,
        "conditions": {"check": "defender_status", "field": "real_time_protection", "expected": True},
    },
    {
        "id": "dev-environment-check",
        "name": "Developer PCs — Weekly Environment Check",
        "description": "Verify developer tools on all dev machines every Monday at 9 AM",
        "group_filter": {"tags": ["developer"]},
        "policy_type": GroupPolicyType.SCHEDULED_SKILL,
        "skill_id": "developer-setup",
        "schedule_cron": "0 9 * * 1",
        "schedule_type": "weekly",
    },
]


class FleetPolicyEngine:
    """Manages fleet-wide policies."""
    
    async def get_device_groups(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> list[dict]:
        """Get all device groups for a user, with computed membership."""
        result = await db.execute(
            select(DeviceGroup).where(DeviceGroup.user_id == user_id)
        )
        groups = result.scalars().all()
        
        group_data = []
        for group in groups:
            # Count devices in this group
            device_count_result = await db.execute(
                select(Device).where(Device.group_id == group.id)
            )
            devices = device_count_result.scalars().all()
            
            group_data.append({
                "id": group.id,
                "name": group.name,
                "group_type": group.group_type,
                "color": group.color,
                "device_count": len(devices),
                "device_names": [d.name for d in devices],
            })
        
        # Also compute auto-groups based on tags
        all_devices_result = await db.execute(
            select(Device).where(Device.user_id == user_id)
        )
        all_devices = all_devices_result.scalars().all()
        
        tag_groups = {}
        for device in all_devices:
            tags = device.tags or []
            for tag in tags:
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(device.name)
        
        for tag, device_names in tag_groups.items():
            group_data.append({
                "id": f"tag:{tag}",
                "name": f"Tag: {tag}",
                "group_type": "tag",
                "color": "#6366f1",
                "device_count": len(device_names),
                "device_names": device_names,
                "is_auto_group": True,
            })
        
        # Add "All Devices" group
        group_data.insert(0, {
            "id": "all",
            "name": "All Devices",
            "group_type": "all",
            "color": "#10b981",
            "device_count": len(all_devices),
            "device_names": [d.name for d in all_devices],
            "is_auto_group": True,
        })
        
        return group_data
    
    async def get_fleet_policies(
        self,
        user_id: str,
    ) -> list[FleetPolicy]:
        """Get all fleet policies for a user."""
        # In production, this reads from the database
        # For now, return templates as defaults
        policies = []
        for template in FLEET_POLICY_TEMPLATES:
            policies.append(FleetPolicy(
                id=template["id"],
                name=template["name"],
                description=template["description"],
                group_id="all",
                group_name="All Devices",
                policy_type=template["policy_type"],
                skill_id=template.get("skill_id"),
                tool_name=template.get("tool_name"),
                parameters=template.get("parameters", {}),
                schedule_cron=template.get("schedule_cron"),
                schedule_type=template.get("schedule_type"),
                conditions=template.get("conditions", {}),
                is_active=True,
            ))
        return policies
    
    async def execute_fleet_policy(
        self,
        db: AsyncSession,
        policy: FleetPolicy,
        user_id: str,
    ) -> dict:
        """Execute a fleet policy — run the skill/command on all matching devices."""
        from app.services.skills.engine import skill_engine
        from app.services.command_queue import command_queue
        
        # Get matching devices
        group_id = policy.group_id
        if group_id == "all":
            result = await db.execute(
                select(Device).where(Device.user_id == user_id)
            )
        elif group_id.startswith("tag:"):
            tag = group_id[4:]
            result = await db.execute(
                select(Device).where(Device.user_id == user_id)
            )
            # Filter by tag in Python (in production, use JSONB query)
            all_devices = result.scalars().all()
            matching = [d for d in all_devices if tag in (d.tags or [])]
            # Create a wrapper that looks like a result
            from sqlalchemy.engine import Result
        else:
            result = await db.execute(
                select(Device).where(
                    Device.user_id == user_id,
                    Device.group_id == group_id,
                )
            )
        
        devices = result.scalars().all()
        
        # Filter to online devices only
        online_devices = [d for d in devices if d.status == "online"]
        
        executed = 0
        errors = 0
        
        for device in online_devices:
            try:
                if policy.skill_id:
                    await skill_engine.execute_skill(
                        db=db,
                        user_id=user_id,
                        device_id=device.id,
                        skill_id=policy.skill_id,
                    )
                    executed += 1
                elif policy.tool_name:
                    await command_queue.enqueue(
                        db=db,
                        user_id=user_id,
                        device_id=device.id,
                        tool_name=policy.tool_name,
                        parameters=policy.parameters,
                    )
                    executed += 1
            except Exception as e:
                logger.error(f"Fleet policy error for device {device.id}: {e}")
                errors += 1
        
        policy.last_executed = datetime.now(timezone.utc)
        policy.execution_count += 1
        
        return {
            "policy_id": policy.id,
            "policy_name": policy.name,
            "total_devices": len(devices),
            "online_devices": len(online_devices),
            "executed": executed,
            "errors": errors,
        }
    
    def get_templates(self) -> list[dict]:
        """Get all fleet policy templates."""
        return FLEET_POLICY_TEMPLATES


fleet_policy_engine = FleetPolicyEngine()
