"""Policy Engine — Automated rules for device management.

Instead of only manual/AI commands, policies run automatically:

    If RAM > 90% for 5 minutes
        → Restart heavy services
        → Notify admin

    If disk > 95%
        → Run cleanup
        → Alert user

    If device offline > 24 hours
        → Send email notification

    If Defender disabled
        → Alert immediately (critical)

Policies are:
    - Condition-based (if/then)
    - Time-based (scheduled checks)
    - Event-based (triggered by events)
"""
from datetime import datetime, timezone
from typing import Optional
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import Policy, PolicyAction
from app.core.logging import get_logger

logger = get_logger(__name__)


# ============= BUILT-IN POLICY TEMPLATES =============

POLICY_TEMPLATES = [
    {
        "id": "high-cpu-alert",
        "name": "High CPU Alert",
        "description": "Alert when CPU usage exceeds threshold",
        "condition": {
            "type": "metric",
            "metric": "cpu_usage",
            "operator": ">",
            "value": 90,
            "duration_minutes": 5,
        },
        "actions": [
            {"type": "notification", "severity": "warning", "message": "CPU usage has exceeded 90% for 5 minutes"},
        ],
        "category": "performance",
        "icon": "🔥",
    },
    {
        "id": "low-disk-alert",
        "name": "Low Disk Space",
        "description": "Alert and cleanup when disk space is critically low",
        "condition": {
            "type": "metric",
            "metric": "disk_percent",
            "operator": ">",
            "value": 95,
        },
        "actions": [
            {"type": "command", "tool": "clean_temp", "parameters": {}},
            {"type": "notification", "severity": "critical", "message": "Disk space critically low — running cleanup"},
        ],
        "category": "storage",
        "icon": "💾",
    },
    {
        "id": "device-offline-alert",
        "name": "Device Offline Alert",
        "description": "Notify when a device has been offline for too long",
        "condition": {
            "type": "status",
            "status": "offline",
            "duration_minutes": 1440,  # 24 hours
        },
        "actions": [
            {"type": "notification", "severity": "warning", "message": "Device has been offline for over 24 hours"},
        ],
        "category": "monitoring",
        "icon": "📡",
    },
    {
        "id": "defender-disabled-alert",
        "name": "Security Alert — Defender Disabled",
        "description": "Critical alert when Windows Defender is disabled",
        "condition": {
            "type": "security",
            "check": "defender_status",
            "field": "real_time_protection",
            "operator": "==",
            "value": False,
        },
        "actions": [
            {"type": "notification", "severity": "critical", "message": "Windows Defender real-time protection is DISABLED!"},
        ],
        "category": "security",
        "icon": "🛡️",
    },
    {
        "id": "high-ram-cleanup",
        "name": "Auto Memory Cleanup",
        "description": "Automatically clean up when RAM usage is high",
        "condition": {
            "type": "metric",
            "metric": "ram_usage",
            "operator": ">",
            "value": 90,
            "duration_minutes": 10,
        },
        "actions": [
            {"type": "command", "tool": "list_processes", "parameters": {"sort_by": "memory", "limit": 10}},
            {"type": "notification", "severity": "warning", "message": "High RAM usage detected — check top memory consumers"},
        ],
        "category": "performance",
        "icon": "🧠",
    },
    {
        "id": "scheduled-cleanup",
        "name": "Auto Weekly Cleanup",
        "description": "Automatically clean temp files every week",
        "condition": {
            "type": "schedule",
            "cron": "0 2 * * 0",  # Sunday 2 AM
        },
        "actions": [
            {"type": "command", "tool": "clean_temp", "parameters": {}},
            {"type": "command", "tool": "flush_dns", "parameters": {}},
        ],
        "category": "maintenance",
        "icon": "🧹",
    },
    {
        "id": "agent-update-auto",
        "name": "Auto Agent Update",
        "description": "Automatically update agent when new version available",
        "condition": {
            "type": "update",
            "check": "agent_version",
            "operator": "<",
            "value": "latest",
        },
        "actions": [
            {"type": "update", "action": "download_and_install"},
        ],
        "category": "maintenance",
        "icon": "📦",
    },
    {
        "id": "gpu-temp-alert",
        "name": "GPU Temperature Alert",
        "description": "Alert when GPU temperature is dangerously high",
        "condition": {
            "type": "metric",
            "metric": "gpu_temperature",
            "operator": ">",
            "value": 85,
            "duration_minutes": 2,
        },
        "actions": [
            {"type": "notification", "severity": "critical", "message": "GPU temperature exceeds 85°C — possible cooling issue"},
        ],
        "category": "hardware",
        "icon": "🌡️",
    },
]


class PolicyEngine:
    """Evaluates and executes policies."""

    async def evaluate_policies(
        self,
        db: AsyncSession,
        device_id: str,
        user_id: str,
        metrics: dict,
    ) -> list[dict]:
        """Evaluate all active policies for a device against current metrics.
        
        Args:
            metrics: Current device metrics {cpu_usage, ram_usage, disk_percent, etc.}
        
        Returns:
            List of triggered policy actions
        """
        result = await db.execute(
            select(Policy).where(
                Policy.user_id == user_id,
                Policy.is_active == True,
            )
        )
        policies = result.scalars().all()

        triggered = []

        for policy in policies:
            condition = policy.condition
            if not condition:
                continue

            triggered_action = await self._evaluate_condition(
                condition=condition,
                metrics=metrics,
                policy=policy,
            )
            if triggered_action:
                triggered.append(triggered_action)

        return triggered

    async def _evaluate_condition(
        self,
        condition: dict,
        metrics: dict,
        policy: Policy,
    ) -> Optional[dict]:
        """Evaluate a single policy condition."""
        cond_type = condition.get("type")

        if cond_type == "metric":
            metric_name = condition.get("metric")
            operator = condition.get("operator")
            threshold = condition.get("value")

            current_value = metrics.get(metric_name)
            if current_value is None:
                return None

            triggered = False
            if operator == ">" and current_value > threshold:
                triggered = True
            elif operator == ">=" and current_value >= threshold:
                triggered = True
            elif operator == "<" and current_value < threshold:
                triggered = True
            elif operator == "<=" and current_value <= threshold:
                triggered = True
            elif operator == "==" and current_value == threshold:
                triggered = True

            if triggered:
                return {
                    "policy_id": policy.id,
                    "policy_name": policy.name,
                    "condition": condition,
                    "current_value": current_value,
                    "threshold": threshold,
                    "actions": policy.actions,
                }

        elif cond_type == "status":
            if metrics.get("status") == condition.get("status"):
                return {
                    "policy_id": policy.id,
                    "policy_name": policy.name,
                    "condition": condition,
                    "actions": policy.actions,
                }

        elif cond_type == "security":
            check = condition.get("check")
            field = condition.get("field")
            operator = condition.get("operator")
            expected = condition.get("value")

            actual = metrics.get(check, {}).get(field)
            if actual is not None:
                if operator == "==" and actual == expected:
                    return {
                        "policy_id": policy.id,
                        "policy_name": policy.name,
                        "condition": condition,
                        "actions": policy.actions,
                    }

        return None

    def get_templates(self) -> list[dict]:
        """Get all policy templates."""
        return POLICY_TEMPLATES

    def get_template(self, template_id: str) -> Optional[dict]:
        """Get a specific policy template."""
        for t in POLICY_TEMPLATES:
            if t["id"] == template_id:
                return t
        return None

    async def create_from_template(
        self,
        db: AsyncSession,
        user_id: str,
        template_id: str,
        device_ids: list[str],
    ) -> list[Policy]:
        """Create policies from a template for specified devices."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        policies = []
        for device_id in device_ids:
            policy = Policy(
                user_id=user_id,
                device_id=device_id,
                name=template["name"],
                description=template["description"],
                condition=template["condition"],
                actions=template["actions"],
                category=template.get("category", "custom"),
                is_active=True,
            )
            db.add(policy)
            policies.append(policy)

        await db.flush()
        return policies


policy_engine = PolicyEngine()
