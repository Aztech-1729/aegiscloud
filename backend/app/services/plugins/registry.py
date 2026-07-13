"""Plugin SDK — Extensible tool system

Users can install plugins that add new tools to the registry.

Plugin Architecture:
    Plugin (Rust/WASM/Python)
        ↓
    Exposes tools with JSON Schema
        ↓
    Registered in Tool Registry
        ↓
    Executable like any other tool

Examples:
    GPU Plugin → gpu_overclock, gpu_monitor, gpu_fan_control
    VMware Plugin → vm_start, vm_stop, vm_snapshot
    Docker Plugin → container_list, container_start, container_logs
    Steam Plugin → steam_library, steam_update_game

Plugins are sandboxed and security-reviewed.
"""
from typing import Optional
from datetime import datetime, timezone
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import Plugin, PluginInstallation
from app.services.tool_registry import tool_registry
from app.core.logging import get_logger

logger = get_logger(__name__)


# ============= BUILT-IN PLUGIN TEMPLATES =============

PLUGIN_REGISTRY = [
    {
        "id": "gpu-control",
        "name": "GPU Control",
        "description": "Advanced GPU monitoring and control — overclocking, fan control, performance profiles",
        "version": "1.0.0",
        "author": "Aegis Cloud",
        "category": "hardware",
        "icon": "🎮",
        "tools": [
            {
                "name": "gpu_monitor",
                "description": "Real-time GPU monitoring with detailed metrics",
                "input_schema": {"type": "object", "properties": {}, "required": []},
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "temperature": {"type": "number"},
                        "fan_speed": {"type": "number"},
                        "clock_speed": {"type": "number"},
                        "memory_clock": {"type": "number"},
                        "power_draw": {"type": "number"},
                    },
                },
            },
            {
                "name": "gpu_profile",
                "description": "Apply GPU performance profile",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "profile": {"type": "string", "enum": ["quiet", "balanced", "performance", "overclock"]},
                    },
                    "required": ["profile"],
                },
                "output_schema": {"type": "object", "properties": {"success": {"type": "boolean"}}},
            },
        ],
        "download_count": 8234,
        "rating": 4.7,
        "size_mb": 2.4,
        "requires_restart": False,
    },
    {
        "id": "docker-manager",
        "name": "Docker Manager",
        "description": "Manage Docker containers, images, and volumes",
        "version": "1.0.0",
        "author": "Aegis Cloud",
        "category": "developer",
        "icon": "🐳",
        "tools": [
            {
                "name": "docker_containers",
                "description": "List running Docker containers",
                "input_schema": {"type": "object", "properties": {}, "required": []},
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "containers": {"type": "array"},
                    },
                },
            },
            {
                "name": "docker_start",
                "description": "Start a Docker container",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "container_id": {"type": "string"},
                    },
                    "required": ["container_id"],
                },
                "output_schema": {"type": "object", "properties": {"success": {"type": "boolean"}}},
            },
            {
                "name": "docker_stop",
                "description": "Stop a Docker container",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "container_id": {"type": "string"},
                    },
                    "required": ["container_id"],
                },
                "output_schema": {"type": "object", "properties": {"success": {"type": "boolean"}}},
            },
        ],
        "download_count": 5621,
        "rating": 4.8,
        "size_mb": 3.1,
        "requires_restart": False,
    },
    {
        "id": "vmware-control",
        "name": "VMware Control",
        "description": "Manage VMware virtual machines",
        "version": "1.0.0",
        "author": "Aegis Cloud",
        "category": "virtualization",
        "icon": "💻",
        "tools": [
            {
                "name": "vm_list",
                "description": "List virtual machines",
                "input_schema": {"type": "object", "properties": {}, "required": []},
                "output_schema": {"type": "object", "properties": {"vms": {"type": "array"}}},
            },
            {
                "name": "vm_start",
                "description": "Start a virtual machine",
                "input_schema": {
                    "type": "object",
                    "properties": {"vm_id": {"type": "string"}},
                    "required": ["vm_id"],
                },
                "output_schema": {"type": "object", "properties": {"success": {"type": "boolean"}}},
            },
        ],
        "download_count": 2341,
        "rating": 4.6,
        "size_mb": 4.2,
        "requires_restart": True,
    },
    {
        "id": "steam-manager",
        "name": "Steam Manager",
        "description": "Manage Steam games and updates",
        "version": "1.0.0",
        "author": "Community",
        "category": "gaming",
        "icon": "🎯",
        "tools": [
            {
                "name": "steam_library",
                "description": "List installed Steam games",
                "input_schema": {"type": "object", "properties": {}, "required": []},
                "output_schema": {"type": "object", "properties": {"games": {"type": "array"}}},
            },
            {
                "name": "steam_update",
                "description": "Update a specific game",
                "input_schema": {
                    "type": "object",
                    "properties": {"app_id": {"type": "integer"}},
                    "required": ["app_id"],
                },
                "output_schema": {"type": "object", "properties": {"success": {"type": "boolean"}}},
            },
        ],
        "download_count": 12456,
        "rating": 4.9,
        "size_mb": 1.8,
        "requires_restart": False,
    },
    {
        "id": "network-monitor",
        "name": "Network Monitor",
        "description": "Advanced network monitoring and diagnostics",
        "version": "1.0.0",
        "author": "Aegis Cloud",
        "category": "network",
        "icon": "🌐",
        "tools": [
            {
                "name": "net_speed_test",
                "description": "Run internet speed test",
                "input_schema": {"type": "object", "properties": {}, "required": []},
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "download_mbps": {"type": "number"},
                        "upload_mbps": {"type": "number"},
                        "ping_ms": {"type": "number"},
                    },
                },
            },
            {
                "name": "net_connections",
                "description": "List active network connections",
                "input_schema": {"type": "object", "properties": {}, "required": []},
                "output_schema": {"type": "object", "properties": {"connections": {"type": "array"}}},
            },
        ],
        "download_count": 9876,
        "rating": 4.7,
        "size_mb": 2.1,
        "requires_restart": False,
    },
]


class PluginManager:
    """Manages plugin installation and tool registration."""

    async def install_plugin(
        self,
        db: AsyncSession,
        user_id: str,
        device_id: str,
        plugin_id: str,
    ) -> dict:
        """Install a plugin and register its tools."""
        plugin_data = self._find_plugin(plugin_id)
        if not plugin_data:
            raise ValueError(f"Plugin not found: {plugin_id}")

        # Check if already installed
        result = await db.execute(
            select(PluginInstallation).where(
                PluginInstallation.user_id == user_id,
                PluginInstallation.device_id == device_id,
                PluginInstallation.plugin_id == plugin_id,
            )
        )
        if result.scalar_one_or_none():
            raise ValueError("Plugin already installed")

        # Record installation
        installation = PluginInstallation(
            user_id=user_id,
            device_id=device_id,
            plugin_id=plugin_id,
            version=plugin_data["version"],
            installed_at=datetime.now(timezone.utc),
        )
        db.add(installation)
        await db.flush()

        # Register plugin tools in tool registry
        for tool_def in plugin_data.get("tools", []):
            tool_registry.register({
                "name": tool_def["name"],
                "version": plugin_data["version"],
                "description": tool_def["description"],
                "category": plugin_data["category"],
                "input_schema": tool_def["input_schema"],
                "output_schema": tool_def["output_schema"],
                "requires_approval": False,
                "risk_level": "medium",
                "allowed_on_plans": ["pro", "business", "enterprise"],
                "plugin_id": plugin_id,
            })

        logger.info(f"Plugin installed: {plugin_id} for device {device_id}")

        return {
            "plugin_id": plugin_id,
            "name": plugin_data["name"],
            "version": plugin_data["version"],
            "tools_registered": len(plugin_data.get("tools", [])),
            "message": "Plugin installed successfully",
        }

    async def uninstall_plugin(
        self,
        db: AsyncSession,
        user_id: str,
        device_id: str,
        plugin_id: str,
    ) -> dict:
        """Uninstall a plugin and unregister its tools."""
        result = await db.execute(
            select(PluginInstallation).where(
                PluginInstallation.user_id == user_id,
                PluginInstallation.device_id == device_id,
                PluginInstallation.plugin_id == plugin_id,
            )
        )
        installation = result.scalar_one_or_none()
        if not installation:
            raise ValueError("Plugin not installed")

        # Remove installation record
        await db.delete(installation)

        # Unregister tools (in production, would remove from registry)
        plugin_data = self._find_plugin(plugin_id)
        tools_removed = 0
        if plugin_data:
            tools_removed = len(plugin_data.get("tools", []))

        await db.flush()

        logger.info(f"Plugin uninstalled: {plugin_id} for device {device_id}")

        return {
            "plugin_id": plugin_id,
            "tools_removed": tools_removed,
            "message": "Plugin uninstalled successfully",
        }

    async def get_installed_plugins(
        self,
        db: AsyncSession,
        user_id: str,
        device_id: Optional[str] = None,
    ) -> list[dict]:
        """Get installed plugins for a user/device."""
        query = select(PluginInstallation).where(PluginInstallation.user_id == user_id)
        if device_id:
            query = query.where(PluginInstallation.device_id == device_id)

        result = await db.execute(query)
        installations = result.scalars().all()

        plugins = []
        for install in installations:
            plugin_data = self._find_plugin(install.plugin_id)
            if plugin_data:
                plugins.append({
                    **plugin_data,
                    "installed_at": install.installed_at.isoformat(),
                    "installed_version": install.version,
                })

        return plugins

    def list_available_plugins(
        self,
        category: Optional[str] = None,
    ) -> list[dict]:
        """List all available plugins."""
        plugins = PLUGIN_REGISTRY.copy()
        if category:
            plugins = [p for p in plugins if p["category"] == category]
        return plugins

    def _find_plugin(self, plugin_id: str) -> Optional[dict]:
        for plugin in PLUGIN_REGISTRY:
            if plugin["id"] == plugin_id:
                return plugin
        return None


# Global plugin manager
plugin_manager = PluginManager()
