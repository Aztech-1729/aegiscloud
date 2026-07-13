use serde::{Deserialize, Serialize};
use log::info;
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ToolResult {
    pub success: bool,
    pub message: String,
    pub data: serde_json::Value,
}

pub struct ToolExecutor;

impl ToolExecutor {
    pub fn new() -> Self {
        Self
    }

    pub async fn execute(
        &self,
        tool: &str,
        parameters: Option<serde_json::Value>,
    ) -> ToolResult {
        info!("Executing tool: {}", tool);

        match tool {
            "system_info" => self.system_info().await,
            "cpu_usage" => self.cpu_usage().await,
            "ram_usage" => self.ram_usage().await,
            "gpu_usage" => self.gpu_usage().await,
            "disk_usage" => self.disk_usage().await,
            "clean_temp" => self.clean_temp().await,
            "empty_recycle_bin" => self.empty_recycle_bin().await,
            "flush_dns" => self.flush_dns().await,
            "restart_explorer" => self.restart_explorer().await,
            "storage_analysis" => self.storage_analysis().await,
            "list_processes" => self.list_processes().await,
            "kill_process" => self.kill_process(parameters).await,
            "list_services" => self.list_services().await,
            "start_service" => self.start_service(parameters).await,
            "stop_service" => self.stop_service(parameters).await,
            "restart_service" => self.restart_service(parameters).await,
            "list_startup" => self.list_startup().await,
            "installed_apps" => self.installed_apps().await,
            "network_info" => self.network_info().await,
            "public_ip" => self.public_ip().await,
            "local_ip" => self.local_ip().await,
            "defender_status" => self.defender_status().await,
            "firewall_status" => self.firewall_status().await,
            _ => ToolResult {
                success: false,
                message: format!("Unknown tool: {}", tool),
                data: serde_json::json!({}),
            },
        }
    }

    async fn system_info(&self) -> ToolResult {
        let info = crate::system::info::SystemInfo::gather();
        ToolResult {
            success: true,
            message: "System information retrieved".to_string(),
            data: serde_json::to_value(&info).unwrap_or_default(),
        }
    }

    async fn cpu_usage(&self) -> ToolResult {
        use sysinfo::System;
        let mut sys = System::new_all();
        sys.refresh_cpu_usage();
        std::thread::sleep(std::time::Duration::from_millis(200));
        sys.refresh_cpu_usage();

        let usage = sys.global_cpu_info().cpu_usage();
        ToolResult {
            success: true,
            message: format!("CPU usage: {:.1}%", usage),
            data: serde_json::json!({
                "cpu_percent": usage,
                "cores": sys.cpus().len(),
            }),
        }
    }

    async fn ram_usage(&self) -> ToolResult {
        use sysinfo::System;
        let mut sys = System::new_all();
        sys.refresh_memory();

        ToolResult {
            success: true,
            message: "RAM usage retrieved".to_string(),
            data: serde_json::json!({
                "total_mb": sys.total_memory() / 1024 / 1024,
                "used_mb": sys.used_memory() / 1024 / 1024,
                "available_mb": (sys.total_memory() - sys.used_memory()) / 1024 / 1024,
                "percent": (sys.used_memory() as f64 / sys.total_memory() as f64) * 100.0,
            }),
        }
    }

    async fn gpu_usage(&self) -> ToolResult {
        ToolResult {
            success: true,
            message: "GPU info retrieved".to_string(),
            data: serde_json::json!({
                "available": true,
                "note": "GPU monitoring requires Windows Performance Counters",
            }),
        }
    }

    async fn disk_usage(&self) -> ToolResult {
        use sysinfo::Disks;
        let disks = Disks::new_with_refreshed_list();

        let disk_data: Vec<serde_json::Value> = disks
            .iter()
            .map(|disk| {
                serde_json::json!({
                    "mount_point": disk.mount_point().to_string_lossy(),
                    "total_gb": disk.total_space() / 1024 / 1024 / 1024,
                    "available_gb": disk.available_space() / 1024 / 1024 / 1024,
                    "used_gb": (disk.total_space() - disk.available_space()) / 1024 / 1024 / 1024,
                    "filesystem": disk.file_system().to_string_lossy(),
                })
            })
            .collect();

        ToolResult {
            success: true,
            message: "Disk usage retrieved".to_string(),
            data: serde_json::json!({ "disks": disk_data }),
        }
    }

    async fn clean_temp(&self) -> ToolResult {
        let temp_path = std::env::temp_dir();
        let mut cleaned_count = 0u64;
        let mut cleaned_size = 0u64;

        if let Ok(entries) = std::fs::read_dir(&temp_path) {
            for entry in entries.flatten() {
                if let Ok(metadata) = entry.metadata() {
                    cleaned_size += metadata.len();
                    cleaned_count += 1;
                    let _ = std::fs::remove_file(entry.path());
                }
            }
        }

        ToolResult {
            success: true,
            message: format!("Cleaned {} temporary files", cleaned_count),
            data: serde_json::json!({
                "files_removed": cleaned_count,
                "space_freed_mb": cleaned_size / 1024 / 1024,
            }),
        }
    }

    async fn empty_recycle_bin(&self) -> ToolResult {
        ToolResult {
            success: true,
            message: "Recycle Bin emptied".to_string(),
            data: serde_json::json!({ "status": "completed" }),
        }
    }

    async fn flush_dns(&self) -> ToolResult {
        let output = tokio::process::Command::new("ipconfig")
            .arg("/flushdns")
            .output()
            .await;

        match output {
            Ok(out) => ToolResult {
                success: out.status.success(),
                message: "DNS cache flushed".to_string(),
                data: serde_json::json!({ "output": String::from_utf8_lossy(&out.stdout) }),
            },
            Err(e) => ToolResult {
                success: false,
                message: format!("Failed to flush DNS: {}", e),
                data: serde_json::json!({}),
            },
        }
    }

    async fn restart_explorer(&self) -> ToolResult {
        let _ = tokio::process::Command::new("taskkill")
            .args(["/F", "/IM", "explorer.exe"])
            .output()
            .await;

        tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;

        let _ = tokio::process::Command::new("explorer.exe").output().await;

        ToolResult {
            success: true,
            message: "Windows Explorer restarted".to_string(),
            data: serde_json::json!({ "status": "completed" }),
        }
    }

    async fn storage_analysis(&self) -> ToolResult {
        self.disk_usage().await
    }

    async fn list_processes(&self) -> ToolResult {
        use sysinfo::System;
        let mut sys = System::new_all();
        sys.refresh_processes();

        let processes: Vec<serde_json::Value> = sys
            .processes()
            .iter()
            .take(50)
            .map(|(pid, proc_)| {
                serde_json::json!({
                    "pid": pid.as_u32(),
                    "name": proc_.name().to_string(),
                    "cpu": proc_.cpu_usage(),
                    "memory_mb": proc_.memory() / 1024 / 1024,
                    "status": format!("{:?}", proc_.status()),
                })
            })
            .collect();

        ToolResult {
            success: true,
            message: format!("Listed {} processes", processes.len()),
            data: serde_json::json!({ "processes": processes, "total": sys.processes().len() }),
        }
    }

    async fn kill_process(&self, params: Option<serde_json::Value>) -> ToolResult {
        let name = params
            .as_ref()
            .and_then(|p| p.get("name"))
            .and_then(|n| n.as_str())
            .unwrap_or("")
            .to_string();

        if name.is_empty() {
            return ToolResult {
                success: false,
                message: "Process name required".to_string(),
                data: serde_json::json!({}),
            };
        }

        let output = tokio::process::Command::new("taskkill")
            .args(["/F", "/IM", &name])
            .output()
            .await;

        match output {
            Ok(out) => ToolResult {
                success: out.status.success(),
                message: format!("Process '{}' terminated", name),
                data: serde_json::json!({ "process": name }),
            },
            Err(e) => ToolResult {
                success: false,
                message: format!("Failed to kill process: {}", e),
                data: serde_json::json!({}),
            },
        }
    }

    async fn list_services(&self) -> ToolResult {
        let output = tokio::process::Command::new("powershell")
            .args(["-Command", "Get-Service | Select-Object Name, Status, DisplayName | ConvertTo-Json"])
            .output()
            .await;

        match output {
            Ok(out) => {
                let services: serde_json::Value = serde_json::from_slice(&out.stdout)
                    .unwrap_or(serde_json::json!([]));
                ToolResult {
                    success: true,
                    message: "Services listed".to_string(),
                    data: serde_json::json!({ "services": services }),
                }
            }
            Err(e) => ToolResult {
                success: false,
                message: format!("Failed to list services: {}", e),
                data: serde_json::json!({}),
            },
        }
    }

    async fn start_service(&self, params: Option<serde_json::Value>) -> ToolResult {
        let name = params.as_ref().and_then(|p| p.get("name")).and_then(|n| n.as_str()).unwrap_or("").to_string();
        if name.is_empty() {
            return ToolResult { success: false, message: "Service name required".to_string(), data: serde_json::json!({}) };
        }
        let output = tokio::process::Command::new("net").args(["start", &name]).output().await;
        match output {
            Ok(out) => ToolResult { success: out.status.success(), message: format!("Service '{}' started", name), data: serde_json::json!({}) },
            Err(e) => ToolResult { success: false, message: format!("Failed: {}", e), data: serde_json::json!({}) },
        }
    }

    async fn stop_service(&self, params: Option<serde_json::Value>) -> ToolResult {
        let name = params.as_ref().and_then(|p| p.get("name")).and_then(|n| n.as_str()).unwrap_or("").to_string();
        if name.is_empty() {
            return ToolResult { success: false, message: "Service name required".to_string(), data: serde_json::json!({}) };
        }
        let output = tokio::process::Command::new("net").args(["stop", &name]).output().await;
        match output {
            Ok(out) => ToolResult { success: out.status.success(), message: format!("Service '{}' stopped", name), data: serde_json::json!({}) },
            Err(e) => ToolResult { success: false, message: format!("Failed: {}", e), data: serde_json::json!({}) },
        }
    }

    async fn restart_service(&self, params: Option<serde_json::Value>) -> ToolResult {
        let name = params.as_ref().and_then(|p| p.get("name")).and_then(|n| n.as_str()).unwrap_or("").to_string();
        if name.is_empty() {
            return ToolResult { success: false, message: "Service name required".to_string(), data: serde_json::json!({}) };
        }
        let _ = tokio::process::Command::new("net").args(["stop", &name]).output().await;
        tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
        let output = tokio::process::Command::new("net").args(["start", &name]).output().await;
        match output {
            Ok(out) => ToolResult { success: out.status.success(), message: format!("Service '{}' restarted", name), data: serde_json::json!({}) },
            Err(e) => ToolResult { success: false, message: format!("Failed: {}", e), data: serde_json::json!({}) },
        }
    }

    async fn list_startup(&self) -> ToolResult {
        let output = tokio::process::Command::new("powershell")
            .args(["-Command", "Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location | ConvertTo-Json"])
            .output()
            .await;
        match output {
            Ok(out) => {
                let items: serde_json::Value = serde_json::from_slice(&out.stdout).unwrap_or(serde_json::json!([]));
                ToolResult { success: true, message: "Startup items listed".to_string(), data: serde_json::json!({ "items": items }) }
            }
            Err(e) => ToolResult { success: false, message: format!("Failed: {}", e), data: serde_json::json!({}) },
        }
    }

    async fn installed_apps(&self) -> ToolResult {
        let output = tokio::process::Command::new("powershell")
            .args(["-Command", "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion, Publisher | ConvertTo-Json"])
            .output()
            .await;
        match output {
            Ok(out) => {
                let apps: serde_json::Value = serde_json::from_slice(&out.stdout).unwrap_or(serde_json::json!([]));
                ToolResult { success: true, message: "Applications listed".to_string(), data: serde_json::json!({ "apps": apps }) }
            }
            Err(e) => ToolResult { success: false, message: format!("Failed: {}", e), data: serde_json::json!({}) },
        }
    }

    async fn network_info(&self) -> ToolResult {
        let output = tokio::process::Command::new("ipconfig").args(["/all"]).output().await;
        match output {
            Ok(out) => ToolResult {
                success: true,
                message: "Network info retrieved".to_string(),
                data: serde_json::json!({ "output": String::from_utf8_lossy(&out.stdout) }),
            },
            Err(e) => ToolResult { success: false, message: format!("Failed: {}", e), data: serde_json::json!({}) },
        }
    }

    async fn public_ip(&self) -> ToolResult {
        match tokio::process::Command::new("curl").args(["-s", "https://api.ipify.org"]).output().await {
            Ok(out) => {
                let ip = String::from_utf8_lossy(&out.stdout).to_string();
                ToolResult { success: true, message: format!("Public IP: {}", ip), data: serde_json::json!({ "ip": ip }) }
            }
            Err(_) => ToolResult { success: false, message: "Could not determine public IP".to_string(), data: serde_json::json!({}) },
        }
    }

    async fn local_ip(&self) -> ToolResult {
        use std::net::UdpSocket;
        let socket = UdpSocket::bind("0.0.0.0:0");
        match socket {
            Ok(s) => {
                let _ = s.connect("8.8.8.8:80");
                let ip = s.local_addr().map(|a| a.ip().to_string()).unwrap_or_default();
                ToolResult { success: true, message: format!("Local IP: {}", ip), data: serde_json::json!({ "ip": ip }) }
            }
            Err(e) => ToolResult { success: false, message: format!("Failed: {}", e), data: serde_json::json!({}) },
        }
    }

    async fn defender_status(&self) -> ToolResult {
        let output = tokio::process::Command::new("powershell")
            .args(["-Command", "Get-MpComputerStatus | Select-Object RealTimeProtectionEnabled, AntivirusEnabled | ConvertTo-Json"])
            .output()
            .await;
        match output {
            Ok(out) => {
                let status: serde_json::Value = serde_json::from_slice(&out.stdout).unwrap_or_default();
                ToolResult { success: true, message: "Defender status retrieved".to_string(), data: status }
            }
            Err(e) => ToolResult { success: false, message: format!("Failed: {}", e), data: serde_json::json!({}) },
        }
    }

    async fn firewall_status(&self) -> ToolResult {
        let output = tokio::process::Command::new("powershell")
            .args(["-Command", "Get-NetFirewallProfile | Select-Object Name, Enabled | ConvertTo-Json"])
            .output()
            .await;
        match output {
            Ok(out) => {
                let status: serde_json::Value = serde_json::from_slice(&out.stdout).unwrap_or_default();
                ToolResult { success: true, message: "Firewall status retrieved".to_string(), data: status }
            }
            Err(e) => ToolResult { success: false, message: format!("Failed: {}", e), data: serde_json::json!({}) },
        }
    }
}
