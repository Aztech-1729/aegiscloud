"""Phase 3: Tool Registry - Strict typed tools with JSON schema validation.

Every tool has:
- Defined input schema (JSON Schema)
- Defined output schema (JSON Schema)
- Risk level
- Approval requirements
- Plan restrictions

This ensures the AI can NEVER invent commands - it can only select
from pre-approved tools with validated parameters.
"""
from typing import Any, Optional
from datetime import datetime, timezone
import json
import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import ToolDefinition


class ToolValidationError(Exception):
    """Raised when tool parameters fail validation."""
    pass


class ToolRegistry:
    """Central registry of all approved tools with strict typing."""

    def __init__(self):
        self._tools: dict[str, dict] = {}
        self._initialize_builtin_tools()

    def _initialize_builtin_tools(self):
        """Register all built-in tools with strict schemas."""

        # ============= SYSTEM TOOLS =============
        self.register({
            "name": "system_info",
            "version": "1.0.0",
            "description": "Get detailed system information including OS, CPU, RAM, disk, and GPU.",
            "category": "system",
            "input_schema": {"type": "object", "properties": {}, "required": []},
            "output_schema": {
                "type": "object",
                "properties": {
                    "hostname": {"type": "string"},
                    "os_name": {"type": "string"},
                    "os_version": {"type": "string"},
                    "cpu_brand": {"type": "string"},
                    "cpu_cores": {"type": "integer"},
                    "total_ram_gb": {"type": "number"},
                    "gpu_info": {"type": "string"},
                    "disk_total_gb": {"type": "number"},
                    "disk_used_gb": {"type": "number"},
                },
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
            "examples": [{"input": {}, "description": "Get full system info"}],
        })

        self.register({
            "name": "cpu_usage",
            "version": "1.0.0",
            "description": "Get current CPU usage percentage and per-core breakdown.",
            "category": "system",
            "input_schema": {"type": "object", "properties": {}, "required": []},
            "output_schema": {
                "type": "object",
                "properties": {
                    "cpu_percent": {"type": "number"},
                    "cores": {"type": "integer"},
                    "per_core": {"type": "array", "items": {"type": "number"}},
                },
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        self.register({
            "name": "ram_usage",
            "version": "1.0.0",
            "description": "Get current memory usage including total, used, and available.",
            "category": "system",
            "input_schema": {"type": "object", "properties": {}, "required": []},
            "output_schema": {
                "type": "object",
                "properties": {
                    "total_mb": {"type": "integer"},
                    "used_mb": {"type": "integer"},
                    "available_mb": {"type": "integer"},
                    "percent": {"type": "number"},
                },
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        self.register({
            "name": "gpu_usage",
            "version": "1.0.0",
            "description": "Get GPU usage, temperature, and VRAM usage.",
            "category": "system",
            "input_schema": {"type": "object", "properties": {}, "required": []},
            "output_schema": {
                "type": "object",
                "properties": {
                    "gpu_percent": {"type": "number"},
                    "temperature_c": {"type": "number"},
                    "vram_total_mb": {"type": "integer"},
                    "vram_used_mb": {"type": "integer"},
                },
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        self.register({
            "name": "disk_usage",
            "version": "1.0.0",
            "description": "Get disk usage for all drives.",
            "category": "system",
            "input_schema": {
                "type": "object",
                "properties": {
                    "drive": {"type": "string", "description": "Specific drive letter (e.g., 'C:'). Omit for all drives."},
                },
                "required": [],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "disks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "mount_point": {"type": "string"},
                                "total_gb": {"type": "number"},
                                "used_gb": {"type": "number"},
                                "available_gb": {"type": "number"},
                            },
                        },
                    },
                },
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        # ============= OPTIMIZATION TOOLS =============
        self.register({
            "name": "clean_temp",
            "version": "1.0.0",
            "description": "Clean temporary files from the system to free up disk space.",
            "category": "optimization",
            "input_schema": {
                "type": "object",
                "properties": {
                    "include_prefetch": {"type": "boolean", "default": True},
                    "include_windows_update": {"type": "boolean", "default": False},
                },
                "required": [],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "files_removed": {"type": "integer"},
                    "space_freed_mb": {"type": "number"},
                },
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        self.register({
            "name": "empty_recycle_bin",
            "version": "1.0.0",
            "description": "Empty the Windows Recycle Bin.",
            "category": "optimization",
            "input_schema": {"type": "object", "properties": {}, "required": []},
            "output_schema": {
                "type": "object",
                "properties": {
                    "items_removed": {"type": "integer"},
                    "space_freed_mb": {"type": "number"},
                },
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        self.register({
            "name": "flush_dns",
            "version": "1.0.0",
            "description": "Flush the DNS resolver cache.",
            "category": "optimization",
            "input_schema": {"type": "object", "properties": {}, "required": []},
            "output_schema": {
                "type": "object",
                "properties": {"success": {"type": "boolean"}},
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        self.register({
            "name": "restart_explorer",
            "version": "1.0.0",
            "description": "Restart Windows Explorer process (taskbar and file manager).",
            "category": "optimization",
            "input_schema": {"type": "object", "properties": {}, "required": []},
            "output_schema": {
                "type": "object",
                "properties": {"success": {"type": "boolean"}},
            },
            "requires_approval": False,
            "risk_level": "medium",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        self.register({
            "name": "storage_analysis",
            "version": "1.0.0",
            "description": "Analyze disk usage and find large files/folders.",
            "category": "optimization",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": "C:\\Users"},
                    "min_size_mb": {"type": "integer", "default": 100},
                    "max_depth": {"type": "integer", "default": 3},
                },
                "required": [],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "large_files": {"type": "array"},
                    "folder_sizes": {"type": "array"},
                    "total_analyzed_gb": {"type": "number"},
                },
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["pro", "business", "enterprise"],
        })

        # ============= PROCESS TOOLS =============
        self.register({
            "name": "list_processes",
            "version": "1.0.0",
            "description": "List all running processes with resource usage.",
            "category": "process",
            "input_schema": {
                "type": "object",
                "properties": {
                    "sort_by": {"type": "string", "enum": ["cpu", "memory", "name"], "default": "cpu"},
                    "limit": {"type": "integer", "default": 50, "minimum": 1, "maximum": 500},
                },
                "required": [],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "processes": {"type": "array"},
                    "total": {"type": "integer"},
                },
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        self.register({
            "name": "kill_process",
            "version": "1.0.0",
            "description": "Terminate a running process by name or PID.",
            "category": "process",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Process name (e.g., 'chrome.exe')"},
                    "pid": {"type": "integer", "description": "Process ID"},
                },
                "required": [],
                "oneOf": [
                    {"required": ["name"]},
                    {"required": ["pid"]},
                ],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "process_name": {"type": "string"},
                    "pid": {"type": "integer"},
                },
            },
            "requires_approval": True,  # Sensitive - requires approval
            "risk_level": "high",
            "allowed_on_plans": ["pro", "business", "enterprise"],
        })

        # ============= SERVICE TOOLS =============
        self.register({
            "name": "list_services",
            "version": "1.0.0",
            "description": "List Windows services and their status.",
            "category": "service",
            "input_schema": {
                "type": "object",
                "properties": {
                    "status_filter": {"type": "string", "enum": ["all", "running", "stopped"], "default": "all"},
                },
                "required": [],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "services": {"type": "array"},
                },
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        self.register({
            "name": "start_service",
            "version": "1.0.0",
            "description": "Start a Windows service by name.",
            "category": "service",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Service name"},
                },
                "required": ["name"],
            },
            "output_schema": {
                "type": "object",
                "properties": {"success": {"type": "boolean"}, "service_name": {"type": "string"}},
            },
            "requires_approval": True,
            "risk_level": "high",
            "allowed_on_plans": ["business", "enterprise"],
        })

        self.register({
            "name": "stop_service",
            "version": "1.0.0",
            "description": "Stop a Windows service by name.",
            "category": "service",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Service name"},
                },
                "required": ["name"],
            },
            "output_schema": {
                "type": "object",
                "properties": {"success": {"type": "boolean"}, "service_name": {"type": "string"}},
            },
            "requires_approval": True,
            "risk_level": "critical",
            "allowed_on_plans": ["business", "enterprise"],
        })

        self.register({
            "name": "restart_service",
            "version": "1.0.0",
            "description": "Restart a Windows service by name.",
            "category": "service",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Service name"},
                },
                "required": ["name"],
            },
            "output_schema": {
                "type": "object",
                "properties": {"success": {"type": "boolean"}, "service_name": {"type": "string"}},
            },
            "requires_approval": True,
            "risk_level": "high",
            "allowed_on_plans": ["business", "enterprise"],
        })

        # ============= STARTUP TOOLS =============
        self.register({
            "name": "list_startup",
            "version": "1.0.0",
            "description": "List startup applications.",
            "category": "startup",
            "input_schema": {"type": "object", "properties": {}, "required": []},
            "output_schema": {
                "type": "object",
                "properties": {"items": {"type": "array"}},
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        self.register({
            "name": "disable_startup",
            "version": "1.0.0",
            "description": "Disable a startup application.",
            "category": "startup",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
                "required": ["name"],
            },
            "output_schema": {
                "type": "object",
                "properties": {"success": {"type": "boolean"}},
            },
            "requires_approval": True,
            "risk_level": "medium",
            "allowed_on_plans": ["pro", "business", "enterprise"],
        })

        # ============= FILE TOOLS =============
        self.register({
            "name": "search_files",
            "version": "1.0.0",
            "description": "Search for files by name or pattern.",
            "category": "file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "path": {"type": "string", "default": "C:\\Users"},
                    "max_results": {"type": "integer", "default": 100, "maximum": 1000},
                },
                "required": ["pattern"],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "files": {"type": "array"},
                    "total_found": {"type": "integer"},
                },
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["pro", "business", "enterprise"],
        })

        self.register({
            "name": "delete_file",
            "version": "1.0.0",
            "description": "Delete a file on the remote system (moves to Recycle Bin).",
            "category": "file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
            "output_schema": {
                "type": "object",
                "properties": {"success": {"type": "boolean"}, "path": {"type": "string"}},
            },
            "requires_approval": True,
            "risk_level": "critical",
            "allowed_on_plans": ["pro", "business", "enterprise"],
        })

        # ============= NETWORK TOOLS =============
        self.register({
            "name": "network_info",
            "version": "1.0.0",
            "description": "Get network adapter information.",
            "category": "network",
            "input_schema": {"type": "object", "properties": {}, "required": []},
            "output_schema": {
                "type": "object",
                "properties": {
                    "adapters": {"type": "array"},
                    "public_ip": {"type": "string"},
                    "local_ip": {"type": "string"},
                },
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        self.register({
            "name": "public_ip",
            "version": "1.0.0",
            "description": "Get the public IP address.",
            "category": "network",
            "input_schema": {"type": "object", "properties": {}, "required": []},
            "output_schema": {
                "type": "object",
                "properties": {"ip": {"type": "string"}},
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        # ============= SOFTWARE TOOLS =============
        self.register({
            "name": "installed_apps",
            "version": "1.0.0",
            "description": "List installed applications.",
            "category": "software",
            "input_schema": {
                "type": "object",
                "properties": {
                    "search": {"type": "string"},
                },
                "required": [],
            },
            "output_schema": {
                "type": "object",
                "properties": {"apps": {"type": "array"}, "total": {"type": "integer"}},
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        self.register({
            "name": "uninstall_app",
            "version": "1.0.0",
            "description": "Uninstall an application by name.",
            "category": "software",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
                "required": ["name"],
            },
            "output_schema": {
                "type": "object",
                "properties": {"success": {"type": "boolean"}, "app_name": {"type": "string"}},
            },
            "requires_approval": True,
            "risk_level": "critical",
            "allowed_on_plans": ["pro", "business", "enterprise"],
        })

        # ============= SECURITY TOOLS =============
        self.register({
            "name": "defender_status",
            "version": "1.0.0",
            "description": "Get Windows Defender status.",
            "category": "security",
            "input_schema": {"type": "object", "properties": {}, "required": []},
            "output_schema": {
                "type": "object",
                "properties": {
                    "real_time_protection": {"type": "boolean"},
                    "antivirus_enabled": {"type": "boolean"},
                    "definitions_up_to_date": {"type": "boolean"},
                },
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        self.register({
            "name": "firewall_status",
            "version": "1.0.0",
            "description": "Get Windows Firewall status.",
            "category": "security",
            "input_schema": {"type": "object", "properties": {}, "required": []},
            "output_schema": {
                "type": "object",
                "properties": {
                    "profiles": {"type": "array"},
                },
            },
            "requires_approval": False,
            "risk_level": "low",
            "allowed_on_plans": ["free", "pro", "business", "enterprise"],
        })

        # ============= MAINTENANCE TOOLS =============
        self.register({
            "name": "run_sfc",
            "version": "1.0.0",
            "description": "Run System File Checker to repair corrupted system files.",
            "category": "maintenance",
            "input_schema": {"type": "object", "properties": {}, "required": []},
            "output_schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "issues_found": {"type": "integer"},
                    "issues_repaired": {"type": "integer"},
                },
            },
            "requires_approval": True,
            "risk_level": "medium",
            "allowed_on_plans": ["pro", "business", "enterprise"],
        })

        self.register({
            "name": "run_dism",
            "version": "1.0.0",
            "description": "Run DISM repair to fix Windows image corruption.",
            "category": "maintenance",
            "input_schema": {"type": "object", "properties": {}, "required": []},
            "output_schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "repair_completed": {"type": "boolean"},
                },
            },
            "requires_approval": True,
            "risk_level": "medium",
            "allowed_on_plans": ["pro", "business", "enterprise"],
        })

    def register(self, tool: dict) -> None:
        """Register a tool in the registry."""
        self._tools[tool["name"]] = tool

    def get_tool(self, name: str) -> Optional[dict]:
        """Get a tool definition by name."""
        return self._tools.get(name)

    def list_tools(self, category: Optional[str] = None, plan: Optional[str] = None) -> list[dict]:
        """List all tools, optionally filtered by category and plan."""
        tools = list(self._tools.values())
        if category:
            tools = [t for t in tools if t["category"] == category]
        if plan:
            tools = [t for t in tools if plan in t.get("allowed_on_plans", [])]
        return tools

    def validate_parameters(self, tool_name: str, parameters: dict) -> dict:
        """Phase 3: Strict parameter validation against JSON schema.
        
        This prevents the AI from sending arbitrary parameters.
        Returns validated and normalized parameters.
        """
        tool = self.get_tool(tool_name)
        if not tool:
            raise ToolValidationError(f"Unknown tool: {tool_name}")

        schema = tool["input_schema"]
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        # Check required fields
        for field in required:
            if field not in parameters:
                raise ToolValidationError(f"Missing required parameter: {field}")

        # Validate and normalize each parameter
        validated = {}
        for key, value in parameters.items():
            if key not in properties:
                raise ToolValidationError(f"Unknown parameter: {key}")

            prop_schema = properties[key]
            expected_type = prop_schema.get("type")

            # Type checking
            if expected_type == "string" and not isinstance(value, str):
                raise ToolValidationError(f"Parameter '{key}' must be a string")
            if expected_type == "integer" and not isinstance(value, int):
                raise ToolValidationError(f"Parameter '{key}' must be an integer")
            if expected_type == "number" and not isinstance(value, (int, float)):
                raise ToolValidationError(f"Parameter '{key}' must be a number")
            if expected_type == "boolean" and not isinstance(value, bool):
                raise ToolValidationError(f"Parameter '{key}' must be a boolean")
            if expected_type == "array" and not isinstance(value, list):
                raise ToolValidationError(f"Parameter '{key}' must be an array")

            # Enum validation
            if "enum" in prop_schema and value not in prop_schema["enum"]:
                raise ToolValidationError(
                    f"Parameter '{key}' must be one of: {prop_schema['enum']}"
                )

            # Min/max validation
            if "minimum" in prop_schema and isinstance(value, (int, float)):
                if value < prop_schema["minimum"]:
                    raise ToolValidationError(
                        f"Parameter '{key}' must be >= {prop_schema['minimum']}"
                    )
            if "maximum" in prop_schema and isinstance(value, (int, float)):
                if value > prop_schema["maximum"]:
                    raise ToolValidationError(
                        f"Parameter '{key}' must be <= {prop_schema['maximum']}"
                    )

            validated[key] = value

        # Apply defaults for missing optional params
        for key, prop_schema in properties.items():
            if key not in validated and "default" in prop_schema:
                validated[key] = prop_schema["default"]

        return validated

    def requires_approval(self, tool_name: str) -> bool:
        """Check if a tool requires approval before execution."""
        tool = self.get_tool(tool_name)
        return tool.get("requires_approval", False) if tool else False

    def get_risk_level(self, tool_name: str) -> str:
        """Get the risk level of a tool."""
        tool = self.get_tool(tool_name)
        return tool.get("risk_level", "low") if tool else "low"

    def is_allowed_on_plan(self, tool_name: str, plan: str) -> bool:
        """Check if a tool is available on the given plan."""
        tool = self.get_tool(tool_name)
        if not tool:
            return False
        return plan in tool.get("allowed_on_plans", [])


# Global registry instance
tool_registry = ToolRegistry()
