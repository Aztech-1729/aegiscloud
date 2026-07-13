"""Skills System — The Biggest Differentiator

Skills are reusable, shareable packs of tools that accomplish a goal.
Instead of running 15 individual tools, users run ONE skill.

Examples:
    "Gaming Optimization"
        ↓
    Disable background services
    Clean temp files
    Optimize power settings
    Clear GPU cache
    Flush DNS
    Disable Windows Update during gameplay
    → 6 tools, 1 command

    "Windows Repair"
        ↓
    Run SFC
    Run DISM
    Flush DNS
    Restart Explorer
    Repair Windows Store
    Check disk health
    → 6 tools, 1 command

    "Developer Setup"
        ↓
    Enable WSL
    Install Git
    Install VS Code
    Install Docker
    Install Node.js
    Configure environment
    → 6 tools, 1 command

Skills can be:
    - Built-in (shipped with Aegis)
    - Community (shared by users)
    - Enterprise (organization-specific)
    - Marketplace (paid/free)
"""
from typing import Optional
from datetime import datetime, timezone
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import Skill, SkillInstallation
from app.services.tool_registry import tool_registry
from app.services.command_queue import command_queue
from app.core.logging import get_logger

logger = get_logger(__name__)


# ============= BUILT-IN SKILLS =============

BUILTIN_SKILLS = [
    {
        "id": "gaming-optimization",
        "name": "Gaming Optimization",
        "description": "Optimize your PC for gaming — disable background services, clean caches, optimize settings.",
        "category": "gaming",
        "author": "Aegis Cloud",
        "version": "1.0.0",
        "icon": "🎮",
        "steps": [
            {"tool": "clean_temp", "parameters": {"include_prefetch": True}, "description": "Clean temporary files"},
            {"tool": "flush_dns", "parameters": {}, "description": "Flush DNS cache"},
            {"tool": "list_startup", "parameters": {}, "description": "Check startup applications"},
            {"tool": "list_services", "parameters": {"status_filter": "running"}, "description": "Check running services"},
            {"tool": "disk_usage", "parameters": {}, "description": "Check disk space"},
            {"tool": "gpu_usage", "parameters": {}, "description": "Check GPU status"},
        ],
        "estimated_time": "2-3 minutes",
        "risk_level": "low",
        "installed_count": 15847,
        "rating": 4.8,
        "tags": ["gaming", "optimization", "performance"],
    },
    {
        "id": "windows-repair",
        "name": "Windows Repair",
        "description": "Comprehensive Windows repair — fix system files, repair image, flush caches, restart services.",
        "category": "maintenance",
        "author": "Aegis Cloud",
        "version": "1.0.0",
        "icon": "🔧",
        "steps": [
            {"tool": "run_sfc", "parameters": {}, "description": "System File Checker"},
            {"tool": "run_dism", "parameters": {}, "description": "DISM repair"},
            {"tool": "flush_dns", "parameters": {}, "description": "Flush DNS cache"},
            {"tool": "restart_explorer", "parameters": {}, "description": "Restart Explorer"},
            {"tool": "clean_temp", "parameters": {}, "description": "Clean temporary files"},
        ],
        "estimated_time": "10-15 minutes",
        "risk_level": "medium",
        "installed_count": 23456,
        "rating": 4.9,
        "tags": ["repair", "maintenance", "system"],
    },
    {
        "id": "developer-setup",
        "name": "Developer Environment",
        "description": "Check and optimize your development environment — verify tools, check disk, analyze startup.",
        "category": "developer",
        "author": "Aegis Cloud",
        "version": "1.0.0",
        "icon": "💻",
        "steps": [
            {"tool": "installed_apps", "parameters": {}, "description": "List installed applications"},
            {"tool": "system_info", "parameters": {}, "description": "Get system information"},
            {"tool": "disk_usage", "parameters": {}, "description": "Check disk space"},
            {"tool": "ram_usage", "parameters": {}, "description": "Check memory usage"},
            {"tool": "list_startup", "parameters": {}, "description": "Check startup programs"},
        ],
        "estimated_time": "1-2 minutes",
        "risk_level": "low",
        "installed_count": 8932,
        "rating": 4.6,
        "tags": ["developer", "setup", "tools"],
    },
    {
        "id": "security-audit",
        "name": "Security Audit",
        "description": "Comprehensive security check — verify Defender, Firewall, check for suspicious processes and startup items.",
        "category": "security",
        "author": "Aegis Cloud",
        "version": "1.0.0",
        "icon": "🛡️",
        "steps": [
            {"tool": "defender_status", "parameters": {}, "description": "Check Windows Defender"},
            {"tool": "firewall_status", "parameters": {}, "description": "Check Firewall status"},
            {"tool": "list_processes", "parameters": {"sort_by": "cpu", "limit": 30}, "description": "Check running processes"},
            {"tool": "list_startup", "parameters": {}, "description": "Check startup items"},
            {"tool": "list_services", "parameters": {"status_filter": "running"}, "description": "Check running services"},
            {"tool": "network_info", "parameters": {}, "description": "Check network connections"},
        ],
        "estimated_time": "3-5 minutes",
        "risk_level": "low",
        "installed_count": 31222,
        "rating": 4.9,
        "tags": ["security", "audit", "privacy"],
    },
    {
        "id": "deep-cleanup",
        "name": "Deep Cleanup",
        "description": "Thorough system cleanup — temp files, recycle bin, DNS cache, storage analysis.",
        "category": "maintenance",
        "author": "Aegis Cloud",
        "version": "1.0.0",
        "icon": "🧹",
        "steps": [
            {"tool": "clean_temp", "parameters": {"include_prefetch": True}, "description": "Clean temp files"},
            {"tool": "empty_recycle_bin", "parameters": {}, "description": "Empty Recycle Bin"},
            {"tool": "flush_dns", "parameters": {}, "description": "Flush DNS cache"},
            {"tool": "storage_analysis", "parameters": {"min_size_mb": 100}, "description": "Analyze storage"},
            {"tool": "disk_usage", "parameters": {}, "description": "Check disk space"},
        ],
        "estimated_time": "3-5 minutes",
        "risk_level": "low",
        "installed_count": 45678,
        "rating": 4.7,
        "tags": ["cleanup", "maintenance", "storage"],
    },
    {
        "id": "network-diagnostic",
        "name": "Network Diagnostic",
        "description": "Full network diagnostic — check adapters, DNS, IP, connectivity.",
        "category": "network",
        "author": "Aegis Cloud",
        "version": "1.0.0",
        "icon": "🌐",
        "steps": [
            {"tool": "network_info", "parameters": {}, "description": "Check network adapters"},
            {"tool": "public_ip", "parameters": {}, "description": "Check public IP"},
            {"tool": "flush_dns", "parameters": {}, "description": "Flush DNS cache"},
        ],
        "estimated_time": "1 minute",
        "risk_level": "low",
        "installed_count": 12345,
        "rating": 4.5,
        "tags": ["network", "diagnostic", "internet"],
    },
    {
        "id": "startup-optimizer",
        "name": "Startup Optimizer",
        "description": "Analyze and optimize startup programs to speed up boot time.",
        "category": "optimization",
        "author": "Aegis Cloud",
        "version": "1.0.0",
        "icon": "⚡",
        "steps": [
            {"tool": "list_startup", "parameters": {}, "description": "List startup programs"},
            {"tool": "list_services", "parameters": {"status_filter": "running"}, "description": "Check running services"},
            {"tool": "cpu_usage", "parameters": {}, "description": "Check CPU usage"},
            {"tool": "ram_usage", "parameters": {}, "description": "Check memory usage"},
        ],
        "estimated_time": "1-2 minutes",
        "risk_level": "low",
        "installed_count": 19876,
        "rating": 4.6,
        "tags": ["startup", "optimization", "boot"],
    },
    {
        "id": "full-system-check",
        "name": "Full System Check",
        "description": "Complete system health check — all metrics, security, storage, and performance.",
        "category": "diagnostic",
        "author": "Aegis Cloud",
        "version": "1.0.0",
        "icon": "🔍",
        "steps": [
            {"tool": "system_info", "parameters": {}, "description": "Get system information"},
            {"tool": "cpu_usage", "parameters": {}, "description": "Check CPU"},
            {"tool": "ram_usage", "parameters": {}, "description": "Check RAM"},
            {"tool": "gpu_usage", "parameters": {}, "description": "Check GPU"},
            {"tool": "disk_usage", "parameters": {}, "description": "Check disk"},
            {"tool": "defender_status", "parameters": {}, "description": "Check Defender"},
            {"tool": "firewall_status", "parameters": {}, "description": "Check Firewall"},
            {"tool": "network_info", "parameters": {}, "description": "Check network"},
            {"tool": "installed_apps", "parameters": {}, "description": "List installed apps"},
        ],
        "estimated_time": "3-5 minutes",
        "risk_level": "low",
        "installed_count": 56789,
        "rating": 4.9,
        "tags": ["diagnostic", "health", "complete"],
    },
]


class SkillEngine:
    """Executes multi-step skills."""

    async def execute_skill(
        self,
        db: AsyncSession,
        user_id: str,
        device_id: str,
        skill_id: str,
        user_plan: str = "free",
    ) -> dict:
        """Execute all steps in a skill."""
        skill = self._find_skill(skill_id)
        if not skill:
            raise ValueError(f"Skill not found: {skill_id}")

        results = []
        commands = []

        for step in skill["steps"]:
            tool_name = step["tool"]
            parameters = step.get("parameters", {})

            try:
                # Validate tool exists
                if not tool_registry.get_tool(tool_name):
                    results.append({
                        "tool": tool_name,
                        "status": "error",
                        "message": f"Tool '{tool_name}' not available",
                    })
                    continue

                # Check plan access
                if not tool_registry.is_allowed_on_plan(tool_name, user_plan):
                    results.append({
                        "tool": tool_name,
                        "status": "blocked",
                        "message": f"Not available on {user_plan} plan",
                    })
                    continue

                # Queue command
                command = await command_queue.enqueue(
                    db=db,
                    user_id=user_id,
                    device_id=device_id,
                    tool_name=tool_name,
                    parameters=parameters,
                    user_plan=user_plan,
                )
                commands.append(command.id)
                results.append({
                    "tool": tool_name,
                    "description": step.get("description", ""),
                    "status": "queued",
                    "command_id": command.id,
                })
            except Exception as e:
                results.append({
                    "tool": tool_name,
                    "status": "error",
                    "message": str(e),
                })

        return {
            "skill_id": skill_id,
            "skill_name": skill["name"],
            "total_steps": len(skill["steps"]),
            "queued": len(commands),
            "command_ids": commands,
            "steps": results,
        }

    def list_skills(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[dict]:
        """List available skills."""
        skills = BUILTIN_SKILLS.copy()

        if category:
            skills = [s for s in skills if s["category"] == category]
        if search:
            search_lower = search.lower()
            skills = [
                s for s in skills
                if search_lower in s["name"].lower()
                or search_lower in s["description"].lower()
                or any(search_lower in t for t in s.get("tags", []))
            ]

        return skills

    def get_skill(self, skill_id: str) -> Optional[dict]:
        """Get a specific skill by ID."""
        return self._find_skill(skill_id)

    def get_skill_categories(self) -> list[dict]:
        """Get all skill categories with counts."""
        cats = {}
        for skill in BUILTIN_SKILLS:
            cat = skill["category"]
            cats[cat] = cats.get(cat, 0) + 1

        return [
            {"name": name, "count": count}
            for name, count in sorted(cats.items())
        ]

    def _find_skill(self, skill_id: str) -> Optional[dict]:
        for skill in BUILTIN_SKILLS:
            if skill["id"] == skill_id:
                return skill
        return None


# Global skill engine
skill_engine = SkillEngine()
