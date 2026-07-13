use serde::{Deserialize, Serialize};
use sysinfo::System;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct SystemInfo {
    pub hostname: String,
    pub os_name: String,
    pub os_version: String,
    pub kernel_version: String,
    pub cpu_brand: String,
    pub cpu_cores: usize,
    pub total_ram_mb: u64,
    pub uptime_secs: u64,
}

impl SystemInfo {
    pub fn gather() -> Self {
        let mut sys = System::new_all();
        sys.refresh_all();

        Self {
            hostname: whoami::fallible::hostname().unwrap_or_else(|_| "unknown".to_string()),
            os_name: System::name().unwrap_or_else(|| "Windows".to_string()),
            os_version: System::os_version().unwrap_or_else(|| "Unknown".to_string()),
            kernel_version: System::kernel_version().unwrap_or_else(|| "Unknown".to_string()),
            cpu_brand: {
                let cpus = sys.cpus();
                cpus.first().map(|c| c.brand().to_string()).unwrap_or_else(|| "Unknown CPU".to_string())
            },
            cpu_cores: sys.cpus().len(),
            total_ram_mb: sys.total_memory() / 1024 / 1024,
            uptime_secs: System::uptime(),
        }
    }
}
