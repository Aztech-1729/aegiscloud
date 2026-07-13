"""Phase 4: AI Pipeline - LLM → Tool Selection → Rust → Result → LLM

The AI NEVER invents commands. The flow is:

User → LLM → Tool Selection (from registry) → Validate → Queue → Rust Agent → Result → LLM → User

This keeps behavior predictable, auditable, and safe.
"""
from typing import Optional
from datetime import datetime, timezone
import json

from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from app.services.tool_registry import tool_registry, ToolValidationError
from app.services.command_queue import command_queue
from app.models.models import Command, CommandStatus, Device, User
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


# Tool descriptions for LLM function calling
TOOL_PROMPTS = {
    "system_info": "Get complete system information (OS, CPU, RAM, GPU, disk)",
    "cpu_usage": "Check current CPU usage percentage",
    "ram_usage": "Check current memory/RAM usage",
    "gpu_usage": "Check GPU usage, temperature, and VRAM",
    "disk_usage": "Check disk space usage on drives",
    "clean_temp": "Clean temporary files to free disk space",
    "empty_recycle_bin": "Empty the Recycle Bin",
    "flush_dns": "Flush the DNS cache to fix network issues",
    "restart_explorer": "Restart Windows Explorer (fixes taskbar/desktop issues)",
    "storage_analysis": "Analyze disk to find large files and folders",
    "list_processes": "List running processes sorted by resource usage",
    "kill_process": "Force-close a specific process by name or PID",
    "list_services": "List Windows services and their status",
    "start_service": "Start a Windows service",
    "stop_service": "Stop a Windows service",
    "restart_service": "Restart a Windows service",
    "list_startup": "List startup applications",
    "disable_startup": "Disable a startup application",
    "search_files": "Search for files by name or pattern",
    "delete_file": "Delete a file (moves to Recycle Bin)",
    "network_info": "Get network adapter information",
    "public_ip": "Get the public IP address",
    "installed_apps": "List installed applications",
    "uninstall_app": "Uninstall an application",
    "defender_status": "Check Windows Defender antivirus status",
    "firewall_status": "Check Windows Firewall status",
    "run_sfc": "Run System File Checker to repair system files",
    "run_dism": "Run DISM to repair Windows image",
}


class AIPipeline:
    """Phase 4: Structured AI pipeline that uses OpenAI function calling to select tools."""

    def __init__(self):
        self.tool_prompts = TOOL_PROMPTS
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_API_BASE,
            )
        else:
            self.client = None

    async def process_message(
        self,
        db: AsyncSession,
        user: User,
        device: Device,
        message: str,
    ) -> dict:
        """Process a user message through the AI pipeline.
        
        Flow:
        1. LLM analyzes intent
        2. Select tool(s) from registry
        3. Validate parameters
        4. Create command(s) in queue
        5. Return response with tool calls
        """
        message_lower = message.lower()

        # Step 1: LLM intent analysis → tool selection
        selected_tools = await self._analyze_intent(message_lower)

        if not selected_tools:
            return {
                "message": await self._general_response(message_lower, device.name),
                "tool_calls": [],
                "command_id": None,
            }

        # Step 2-4: Validate and queue each tool
        tool_calls = []
        command_id = None

        for tool_info in selected_tools:
            tool_name = tool_info["name"]
            params = tool_info.get("parameters", {})

            try:
                # Validate against tool registry
                validated = tool_registry.validate_parameters(tool_name, params)

                # Check plan access
                if not tool_registry.is_allowed_on_plan(tool_name, user.plan.value):
                    tool_calls.append({
                        "tool": tool_name,
                        "status": "blocked",
                        "reason": f"Not available on {user.plan.value} plan",
                    })
                    continue

                # Check if approval needed
                needs_approval = tool_registry.requires_approval(tool_name)

                # Queue command
                command = await command_queue.enqueue(
                    db=db,
                    user_id=user.id,
                    device_id=device.id,
                    tool_name=tool_name,
                    parameters=validated,
                    user_plan=user.plan.value,
                )
                command_id = command.id

                tool_calls.append({
                    "tool": tool_name,
                    "status": "approval_pending" if needs_approval else "queued",
                    "command_id": command.id,
                })

            except ToolValidationError as e:
                tool_calls.append({
                    "tool": tool_name,
                    "status": "validation_failed",
                    "reason": str(e),
                })
            except ValueError as e:
                tool_calls.append({
                    "tool": tool_name,
                    "status": "failed",
                    "reason": str(e),
                })

        # Step 5: Generate response
        response_message = await self._generate_response(message_lower, selected_tools, device.name, tool_calls)

        return {
            "message": response_message,
            "tool_calls": tool_calls,
            "command_id": command_id,
        }

    async def _analyze_intent(self, message: str) -> list[dict]:
        """Phase 4: Map natural language to tool calls using OpenAI."""
        if not self.client:
            return self._fallback_analyze_intent(message)
            
        tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": t_name,
                    "description": t_desc,
                    "parameters": {"type": "object", "properties": {}}
                }
            }
            for t_name, t_desc in self.tool_prompts.items()
        ]
        
        # Add parameter schemas for specific tools
        for t in tools_schema:
            if t["function"]["name"] == "kill_process":
                t["function"]["parameters"]["properties"] = {"name": {"type": "string"}}
                t["function"]["parameters"]["required"] = ["name"]
            elif t["function"]["name"] == "list_processes":
                t["function"]["parameters"]["properties"] = {"sort_by": {"type": "string"}, "limit": {"type": "integer"}}
            elif t["function"]["name"] == "search_files":
                t["function"]["parameters"]["properties"] = {"pattern": {"type": "string"}}
            elif t["function"]["name"] == "uninstall_app":
                t["function"]["parameters"]["properties"] = {"name": {"type": "string"}}
            elif t["function"]["name"] == "storage_analysis":
                t["function"]["parameters"]["properties"] = {"min_size_mb": {"type": "integer"}}

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are Aegis AI Optimizer. You select the necessary tools to fulfill the user's request on their computer. ONLY select tools that are absolutely necessary. If no tools are needed, just chat with the user."},
                    {"role": "user", "content": message}
                ],
                tools=tools_schema,
                tool_choice="auto",
            )
            
            message_obj = response.choices[0].message
            if message_obj.tool_calls:
                return [
                    {
                        "name": call.function.name,
                        "parameters": json.loads(call.function.arguments) if call.function.arguments else {}
                    }
                    for call in message_obj.tool_calls
                ]
            return []
        except Exception as e:
            logger.error(f"OpenAI Intent error: {e}")
            return self._fallback_analyze_intent(message)

    def _fallback_analyze_intent(self, message: str) -> list[dict]:
        """Fallback when LLM is down."""
        tools = []

        # Performance diagnostics
        if any(w in message for w in ["slow", "lag", "freeze", "performance", "speed"]):
            tools = [
                {"name": "cpu_usage", "parameters": {}},
                {"name": "ram_usage", "parameters": {}},
                {"name": "disk_usage", "parameters": {}},
            ]

        # Temp cleanup
        elif any(w in message for w in ["clean temp", "temp file", "cleanup", "free space"]):
            tools = [{"name": "clean_temp", "parameters": {}}]

        # Recycle bin
        elif "recycle" in message:
            tools = [{"name": "empty_recycle_bin", "parameters": {}}]

        # Explorer issues
        elif any(w in message for w in ["explorer", "taskbar", "start menu", "desktop not showing"]):
            tools = [{"name": "restart_explorer", "parameters": {}}]

        # Process management
        elif any(w in message for w in ["process", "running", "what's using"]):
            tools = [{"name": "list_processes", "parameters": {"sort_by": "cpu", "limit": 20}}]

        # Kill process
        elif any(w in message for w in ["kill", "force close", "end task", "terminate"]):
            # Extract process name if possible
            process_name = self._extract_process_name(message)
            if process_name:
                tools = [{"name": "kill_process", "parameters": {"name": process_name}}]
            else:
                tools = [{"name": "list_processes", "parameters": {"sort_by": "cpu", "limit": 20}}]

        # Installed apps
        elif any(w in message for w in ["installed", "software", "apps", "programs"]):
            tools = [{"name": "installed_apps", "parameters": {}}]

        # Uninstall
        elif any(w in message for w in ["uninstall", "remove app", "delete program"]):
            app_name = self._extract_app_name(message)
            if app_name:
                tools = [{"name": "uninstall_app", "parameters": {"name": app_name}}]
            else:
                tools = [{"name": "installed_apps", "parameters": {}}]

        # Startup
        elif any(w in message for w in ["startup", "boot", "start with windows"]):
            tools = [{"name": "list_startup", "parameters": {}}]

        # Storage analysis
        elif any(w in message for w in ["large files", "storage", "disk space", "what's taking"]):
            tools = [{"name": "storage_analysis", "parameters": {"min_size_mb": 100}}]

        # Security
        elif any(w in message for w in ["security", "defender", "antivirus", "virus", "malware"]):
            tools = [
                {"name": "defender_status", "parameters": {}},
                {"name": "firewall_status", "parameters": {}},
            ]

        # Network
        elif any(w in message for w in ["network", "ip address", "internet", "wifi", "connection"]):
            tools = [
                {"name": "network_info", "parameters": {}},
                {"name": "public_ip", "parameters": {}},
            ]

        # DNS
        elif "dns" in message:
            tools = [{"name": "flush_dns", "parameters": {}}]

        # Services
        elif any(w in message for w in ["service", "services"]):
            tools = [{"name": "list_services", "parameters": {"status_filter": "all"}}]

        # System repair
        elif any(w in message for w in ["sfc", "repair", "corrupt", "system file"]):
            tools = [{"name": "run_sfc", "parameters": {}}]

        elif "dism" in message:
            tools = [{"name": "run_dism", "parameters": {}}]

        # File search
        elif any(w in message for w in ["find file", "search file", "where is"]):
            pattern = self._extract_search_pattern(message)
            if pattern:
                tools = [{"name": "search_files", "parameters": {"pattern": pattern}}]

        # General system info
        elif any(w in message for w in ["system info", "specs", "what do i have", "hardware"]):
            tools = [{"name": "system_info", "parameters": {}}]

        return tools

    async def _generate_response(
        self,
        message: str,
        selected_tools: list[dict],
        device_name: str,
        tool_calls: list[dict],
    ) -> str:
        """Generate a natural language response for the user via LLM."""
        if not self.client:
            return self._fallback_generate_response(message, selected_tools, device_name, tool_calls)
            
        tool_desc = [f"{t['name']} ({t.get('parameters', {})})" for t in selected_tools]
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": f"You are Aegis AI Optimizer assisting with device '{device_name}'. The user requested an action. You have queued the following tools to run on their device: {tool_desc}. Write a short, professional, and confident response telling the user what you are doing (e.g. 'I am analyzing your storage...', 'I have queued a process kill for...'). Do not output markdown code blocks. Keep it to 1-2 sentences."},
                    {"role": "user", "content": message}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI Generate error: {e}")
            return self._fallback_generate_response(message, selected_tools, device_name, tool_calls)

    def _fallback_generate_response(
        self,
        message: str,
        selected_tools: list[dict],
        device_name: str,
        tool_calls: list[dict],
    ) -> str:
        tool_names = [t["name"] for t in selected_tools]

        if "clean_temp" in tool_names:
            return (
                f"I'll clean temporary files on **{device_name}** to free up disk space. "
                "This is safe — it only removes files Windows no longer needs."
            )

        if "cpu_usage" in tool_names and "ram_usage" in tool_names:
            return (
                f"I'm checking the performance of **{device_name}**. "
                "I'll look at CPU, memory, and disk usage to identify any bottlenecks."
            )

        if "restart_explorer" in tool_names:
            return (
                f"I'll restart Windows Explorer on **{device_name}**. "
                "Your taskbar and desktop will briefly flash — this is normal."
            )

        if "list_processes" in tool_names:
            return (
                f"Here are the running processes on **{device_name}**, sorted by resource usage. "
                "Let me know if you want to close any of them."
            )

        if "defender_status" in tool_names:
            return (
                f"Checking security status on **{device_name}**. "
                "I'll verify Windows Defender and Firewall are active."
            )

        if "installed_apps" in tool_names:
            return f"Scanning installed applications on **{device_name}**..."

        if "storage_analysis" in tool_names:
            return (
                f"Analyzing storage on **{device_name}** to find large files and folders. "
                "This may take a moment."
            )

        if "run_sfc" in tool_names:
            return (
                f"Running System File Checker on **{device_name}**. "
                "This will scan for and repair corrupted Windows system files. "
                "It may take several minutes."
            )

        # Generic response
        tool_descriptions = [
            self.tool_prompts.get(t["name"], t["name"])
            for t in selected_tools
        ]
        return (
            f"I'll help with that on **{device_name}**. "
            f"Running: {', '.join(tool_descriptions[:3])}."
        )

    async def _general_response(self, message: str, device_name: str) -> str:
        """Response when no specific tool is matched via LLM."""
        if not self.client:
            return self._fallback_general_response(message, device_name)
            
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": f"You are Aegis AI Optimizer assisting with device '{device_name}'. Provide a helpful, concise answer to the user's message since no specific system tools were needed for this request."},
                    {"role": "user", "content": message}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI General Response error: {e}")
            return self._fallback_general_response(message, device_name)

    def _fallback_general_response(self, message: str, device_name: str) -> str:
        """Response when no specific tool is matched."""
        return (
            f"I can help you manage **{device_name}**. Here are some things I can do:\n\n"
            "• **Check performance** — CPU, RAM, disk usage\n"
            "• **Clean up** — temp files, recycle bin, storage analysis\n"
            "• **Manage processes** — list running apps, force-close\n"
            "• **Services** — list, start, stop Windows services\n"
            "• **Security** — check Defender and Firewall status\n"
            "• **Network** — check connection, IP address, flush DNS\n"
            "• **System repair** — SFC and DISM\n"
            "• **Software** — list installed apps, uninstall\n\n"
            "What would you like me to do?"
        )

    def _extract_process_name(self, message: str) -> Optional[str]:
        """Extract a process name from natural language."""
        import re
        # Look for common patterns like "chrome", "chrome.exe", "Chrome"
        match = re.search(r'(?:kill|close|end|terminate)\s+(\w+\.?\w*)', message, re.IGNORECASE)
        if match:
            name = match.group(1).lower()
            if not name.endswith('.exe'):
                name += '.exe'
            return name
        return None

    def _extract_app_name(self, message: str) -> Optional[str]:
        """Extract an application name from natural language."""
        import re
        match = re.search(
            r'(?:uninstall|remove|delete)\s+(.+?)(?:\s+from|\s+on|\s+please|$)',
            message, re.IGNORECASE
        )
        if match:
            return match.group(1).strip()
        return None

    def _extract_search_pattern(self, message: str) -> Optional[str]:
        """Extract a file search pattern from natural language."""
        import re
        match = re.search(
            r'(?:find|search|where is|looking for)\s+(.+?)(?:\s+on|\s+in|\s+file|$)',
            message, re.IGNORECASE
        )
        if match:
            return match.group(1).strip()
        return None


# Global AI pipeline instance
ai_pipeline = AIPipeline()
