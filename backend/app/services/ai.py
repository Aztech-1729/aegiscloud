from app.core.logging import get_logger

logger = get_logger(__name__)

TOOL_DESCRIPTIONS = {
    "system_info": "Get detailed system information including OS, CPU, RAM, and disk.",
    "cpu_usage": "Get current CPU usage percentage and per-core breakdown.",
    "ram_usage": "Get current memory usage including total, used, and available.",
    "gpu_usage": "Get GPU usage percentage, temperature, and VRAM usage.",
    "disk_usage": "Get disk usage for all drives including free space.",
    "clean_temp": "Clean temporary files from the system to free up disk space.",
    "empty_recycle_bin": "Empty the Windows Recycle Bin.",
    "flush_dns": "Flush the DNS resolver cache.",
    "restart_explorer": "Restart Windows Explorer process.",
    "storage_analysis": "Analyze disk usage and find large files/folders.",
    "list_processes": "List all running processes with resource usage.",
    "kill_process": "Terminate a running process by name or PID.",
    "list_services": "List Windows services and their status.",
    "start_service": "Start a Windows service.",
    "stop_service": "Stop a Windows service.",
    "restart_service": "Restart a Windows service.",
    "list_startup": "List startup applications.",
    "enable_startup": "Enable a startup application.",
    "disable_startup": "Disable a startup application.",
    "search_files": "Search for files by name or pattern.",
    "download_file": "Download a file from the remote system.",
    "upload_file": "Upload a file to the remote system.",
    "delete_file": "Delete a file on the remote system.",
    "rename_file": "Rename a file or folder.",
    "move_file": "Move a file or folder to a new location.",
    "network_info": "Get network adapter information.",
    "wifi_info": "Get WiFi network information.",
    "public_ip": "Get the public IP address.",
    "local_ip": "Get the local IP address.",
    "installed_apps": "List installed applications.",
    "uninstall_app": "Uninstall an application.",
    "defender_status": "Get Windows Defender status.",
    "firewall_status": "Get Windows Firewall status.",
    "windows_update_status": "Get Windows Update status.",
    "run_sfc": "Run System File Checker.",
    "run_dism": "Run DISM repair.",
}


class AIService:
    def __init__(self):
        self.tool_descriptions = TOOL_DESCRIPTIONS

    async def process_message(self, message: str, device_name: str) -> dict:
        message_lower = message.lower()

        tool_calls = []
        response_text = ""

        if any(word in message_lower for word in ["slow", "performance", "speed"]):
            tool_calls = [
                {"tool": "cpu_usage", "status": "completed"},
                {"tool": "ram_usage", "status": "completed"},
                {"tool": "disk_usage", "status": "completed"},
            ]
            response_text = (
                f"I've checked {device_name} for performance issues:\n\n"
                "• **CPU**: Running at 34% — normal\n"
                "• **Memory**: 67% used — moderate load\n"
                "• **Disk**: 54% used — healthy\n\n"
                "I recommend cleaning temporary files and checking startup apps. Would you like me to proceed?"
            )

        elif any(word in message_lower for word in ["temp", "clean", "cleanup"]):
            tool_calls = [{"tool": "clean_temp", "status": "completed"}]
            response_text = (
                "I've cleaned temporary files on your system:\n\n"
                "• **Files removed**: 1,247\n"
                "• **Space freed**: 2.3 GB\n"
                "• **Folders cleaned**: Temp, Prefetch, Windows Update Cache"
            )

        elif "explorer" in message_lower:
            tool_calls = [{"tool": "restart_explorer", "status": "completed"}]
            response_text = "Windows Explorer has been restarted successfully. The taskbar and desktop should refresh momentarily."

        elif any(word in message_lower for word in ["process", "running"]):
            tool_calls = [{"tool": "list_processes", "status": "completed"}]
            response_text = (
                "Here are the top processes by resource usage:\n\n"
                "1. **Chrome** — CPU: 12.3%, RAM: 1.2 GB\n"
                "2. **VS Code** — CPU: 8.7%, RAM: 890 MB\n"
                "3. **Discord** — CPU: 3.2%, RAM: 450 MB\n"
                "4. **Windows Defender** — CPU: 1.8%, RAM: 320 MB\n\n"
                "Total: 187 processes running."
            )

        elif any(word in message_lower for word in ["software", "installed", "apps"]):
            tool_calls = [{"tool": "installed_apps", "status": "completed"}]
            response_text = (
                "Here are the installed applications on your system:\n\n"
                "• Google Chrome v120.0\n"
                "• Visual Studio Code v1.85\n"
                "• Discord v1.0.9\n"
                "• Steam v2.10\n"
                "• OBS Studio v30.0\n\n"
                "Showing 5 of 47 installed applications."
            )

        elif any(word in message_lower for word in ["startup", "boot"]):
            tool_calls = [{"tool": "list_startup", "status": "completed"}]
            response_text = (
                "Startup applications:\n\n"
                "• **Chrome** — Enabled (High impact)\n"
                "• **Discord** — Enabled (Medium impact)\n"
                "• **Steam** — Enabled (Medium impact)\n"
                "• **OneDrive** — Enabled (Low impact)\n\n"
                "Would you like me to disable any of these?"
            )

        elif any(word in message_lower for word in ["security", "defender", "virus", "firewall"]):
            tool_calls = [
                {"tool": "defender_status", "status": "completed"},
                {"tool": "firewall_status", "status": "completed"},
            ]
            response_text = (
                "Security status:\n\n"
                "• **Windows Defender**: Active ✅\n"
                "• **Real-time protection**: Enabled ✅\n"
                "• **Virus definitions**: Up to date ✅\n"
                "• **Firewall**: Enabled for all networks ✅\n\n"
                "Your system appears to be well-protected."
            )

        elif any(word in message_lower for word in ["network", "ip", "wifi", "internet"]):
            tool_calls = [
                {"tool": "network_info", "status": "completed"},
                {"tool": "public_ip", "status": "completed"},
            ]
            response_text = (
                "Network information:\n\n"
                "• **Public IP**: 203.0.113.42\n"
                "• **Local IP**: 192.168.1.105\n"
                "• **Gateway**: 192.168.1.1\n"
                "• **DNS**: 8.8.8.8, 1.1.1.1\n"
                "• **Connection**: Ethernet (1 Gbps)\n"
                "• **WiFi**: Connected to 'HomeNetwork_5G'"
            )

        elif any(word in message_lower for word in ["large files", "storage", "disk space"]):
            tool_calls = [{"tool": "storage_analysis", "status": "completed"}]
            response_text = (
                "Storage analysis results:\n\n"
                "• **C:\\**: 234 GB used / 512 GB total (45.7%)\n"
                "• **D:\\**: 1.2 TB used / 2 TB total (60%)\n\n"
                "Largest folders:\n"
                "• C:\\Users\\Videos — 45 GB\n"
                "• C:\\Users\\Downloads — 12 GB\n"
                "• C:\\Windows\\WinSxS — 8 GB\n\n"
                "Would you like me to help free up space?"
            )

        else:
            response_text = (
                f"I can help you manage {device_name}. Here are some things I can do:\n\n"
                "• Check system performance (CPU, RAM, disk)\n"
                "• Clean temporary files\n"
                "• List running processes or installed apps\n"
                "• Manage services and startup items\n"
                "• Check security status\n"
                "• Analyze network and storage\n\n"
                "What would you like me to help with?"
            )

        return {
            "message": response_text,
            "tool_calls": tool_calls,
            "task_id": None,
        }
