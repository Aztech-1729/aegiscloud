//! Capability Layer - Abstraction between plugins and OS APIs

use crate::capabilities::{Capability, CapabilityContext, CapabilityError};
use serde_json::Value;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum CapabilityLayerError {
    #[error("Capability denied: {0}")]
    CapabilityDenied(#[from] CapabilityError),
    
    #[error("OS error: {0}")]
    OsError(String),
    
    #[error("Invalid parameter: {0}")]
    InvalidParameter(String),
}

/// Capability layer context
pub struct CapabilityLayer {
    context: CapabilityContext,
}

impl CapabilityLayer {
    pub fn new(context: CapabilityContext) -> Self {
        Self { context }
    }
    
    pub fn filesystem(&mut self) -> FileSystemCapability<'_> {
        FileSystemCapability { context: &mut self.context }
    }
    
    pub fn registry(&mut self) -> RegistryCapability<'_> {
        RegistryCapability { context: &mut self.context }
    }
    
    pub fn network(&mut self) -> NetworkCapability<'_> {
        NetworkCapability { context: &mut self.context }
    }
    
    pub fn process(&mut self) -> ProcessCapability<'_> {
        ProcessCapability { context: &mut self.context }
    }
    
    pub fn service(&mut self) -> ServiceCapability<'_> {
        ServiceCapability { context: &mut self.context }
    }
    
    pub fn system(&mut self) -> SystemCapability<'_> {
        SystemCapability { context: &mut self.context }
    }
}

/// Filesystem capability interface
pub struct FileSystemCapability<'a> {
    context: &'a mut CapabilityContext,
}

impl<'a> FileSystemCapability<'a> {
    pub async fn read(&mut self, path: &str) -> Result<Vec<u8>, CapabilityLayerError> {
        self.context.require(Capability::FilesystemRead)?;
        
        if !is_path_allowed(path) {
            return Err(CapabilityLayerError::CapabilityDenied(
                CapabilityError::Denied(Capability::FilesystemRead)
            ));
        }
        
        tokio::fs::read(path)
            .await
            .map_err(|e| CapabilityLayerError::OsError(e.to_string()))
    }
    
    pub async fn read_string(&mut self, path: &str) -> Result<String, CapabilityLayerError> {
        let bytes = self.read(path).await?;
        String::from_utf8(bytes)
            .map_err(|e| CapabilityLayerError::OsError(e.to_string()))
    }
    
    pub async fn write(&mut self, path: &str, contents: &[u8]) -> Result<(), CapabilityLayerError> {
        self.context.require(Capability::FilesystemWrite)?;
        
        if !is_path_allowed(path) {
            return Err(CapabilityLayerError::CapabilityDenied(
                CapabilityError::Denied(Capability::FilesystemWrite)
            ));
        }
        
        tokio::fs::write(path, contents)
            .await
            .map_err(|e| CapabilityLayerError::OsError(e.to_string()))
    }
    
    pub async fn write_temp(&mut self, filename: &str, contents: &[u8]) -> Result<std::path::PathBuf, CapabilityLayerError> {
        self.context.require(Capability::FilesystemWriteTemp)?;
        
        let temp_dir = std::env::temp_dir().join("aegis-plugins").join(self.context.plugin_id());
        tokio::fs::create_dir_all(&temp_dir)
            .await
            .map_err(|e| CapabilityLayerError::OsError(e.to_string()))?;
        
        let path = temp_dir.join(filename);
        tokio::fs::write(&path, contents)
            .await
            .map_err(|e| CapabilityLayerError::OsError(e.to_string()))?;
        
        Ok(path)
    }
    
    pub async fn delete(&mut self, path: &str) -> Result<(), CapabilityLayerError> {
        self.context.require(Capability::FilesystemDelete)?;
        
        if !is_path_allowed(path) {
            return Err(CapabilityLayerError::CapabilityDenied(
                CapabilityError::Denied(Capability::FilesystemDelete)
            ));
        }
        
        tokio::fs::remove_file(path)
            .await
            .map_err(|e| CapabilityLayerError::OsError(e.to_string()))
    }
    
    pub async fn list_dir(&mut self, path: &str) -> Result<Vec<std::path::PathBuf>, CapabilityLayerError> {
        self.context.require(Capability::FilesystemRead)?;
        
        if !is_path_allowed(path) {
            return Err(CapabilityLayerError::CapabilityDenied(
                CapabilityError::Denied(Capability::FilesystemRead)
            ));
        }
        
        let mut entries = Vec::new();
        let mut dir = tokio::fs::read_dir(path)
            .await
            .map_err(|e| CapabilityLayerError::OsError(e.to_string()))?;
        
        while let Some(entry) = dir.next_entry()
            .await
            .map_err(|e| CapabilityLayerError::OsError(e.to_string()))?
        {
            entries.push(entry.path());
        }
        
        Ok(entries)
    }
    
    pub async fn exists(&mut self, path: &str) -> Result<bool, CapabilityLayerError> {
        self.context.require(Capability::FilesystemRead)?;
        
        if !is_path_allowed(path) {
            return Err(CapabilityLayerError::CapabilityDenied(
                CapabilityError::Denied(Capability::FilesystemRead)
            ));
        }
        
        tokio::fs::metadata(path)
            .await
            .map(|_| true)
            .or_else(|_| Ok(false))
    }
    
    pub async fn metadata(&mut self, path: &str) -> Result<std::fs::Metadata, CapabilityLayerError> {
        self.context.require(Capability::FilesystemRead)?;
        
        if !is_path_allowed(path) {
            return Err(CapabilityLayerError::CapabilityDenied(
                CapabilityError::Denied(Capability::FilesystemRead)
            ));
        }
        
        tokio::fs::metadata(path)
            .await
            .map_err(|e| CapabilityLayerError::OsError(e.to_string()))
    }
}

/// Registry capability interface
pub struct RegistryCapability<'a> {
    context: &'a mut CapabilityContext,
}

impl<'a> RegistryCapability<'a> {
    pub async fn read(&mut self, path: &str, value_name: &str) -> Result<Value, CapabilityLayerError> {
        self.context.require(Capability::RegistryRead)?;
        Err(CapabilityLayerError::OsError("Registry read not implemented".to_string()))
    }
    
    pub async fn write(&mut self, path: &str, value_name: &str, value: Value) -> Result<(), CapabilityLayerError> {
        self.context.require(Capability::RegistryWrite)?;
        Err(CapabilityLayerError::OsError("Registry write not implemented".to_string()))
    }
    
    pub async fn delete(&mut self, path: &str) -> Result<(), CapabilityLayerError> {
        self.context.require(Capability::RegistryDelete)?;
        Err(CapabilityLayerError::OsError("Registry delete not implemented".to_string()))
    }
    
    pub async fn list_keys(&mut self, path: &str) -> Result<Vec<String>, CapabilityLayerError> {
        self.context.require(Capability::RegistryRead)?;
        Err(CapabilityLayerError::OsError("Registry list not implemented".to_string()))
    }
}

/// Network capability interface
pub struct NetworkCapability<'a> {
    context: &'a mut CapabilityContext,
}

impl<'a> NetworkCapability<'a> {
    pub async fn ping(&mut self, host: &str) -> Result<bool, CapabilityLayerError> {
        self.context.require(Capability::NetworkPing)?;
        Err(CapabilityLayerError::OsError("Ping not implemented".to_string()))
    }
    
    pub async fn http_get(&mut self, url: &str) -> Result<String, CapabilityLayerError> {
        self.context.require(Capability::NetworkHttp)?;
        Err(CapabilityLayerError::OsError("HTTP not implemented".to_string()))
    }
    
    pub async fn http_post(&mut self, url: &str, body: &str) -> Result<String, CapabilityLayerError> {
        self.context.require(Capability::NetworkHttp)?;
        Err(CapabilityLayerError::OsError("HTTP POST not implemented".to_string()))
    }
    
    pub async fn dns_lookup(&mut self, hostname: &str) -> Result<Vec<std::net::IpAddr>, CapabilityLayerError> {
        self.context.require(Capability::NetworkDns)?;
        Err(CapabilityLayerError::OsError("DNS lookup not implemented".to_string()))
    }
    
    pub async fn tcp_connect(&mut self, host: &str, port: u16) -> Result<tokio::net::TcpStream, CapabilityLayerError> {
        self.context.require(Capability::NetworkTcp)?;
        
        tokio::net::TcpStream::connect(format!("{}:{}", host, port))
            .await
            .map_err(|e| CapabilityLayerError::OsError(e.to_string()))
    }
}

/// Process capability interface
pub struct ProcessCapability<'a> {
    context: &'a mut CapabilityContext,
}

impl<'a> ProcessCapability<'a> {
    pub async fn list(&mut self) -> Result<Vec<ProcessInfo>, CapabilityLayerError> {
        self.context.require(Capability::ProcessList)?;
        Err(CapabilityLayerError::OsError("Process list not implemented".to_string()))
    }
    
    pub async fn get(&mut self, pid: u32) -> Result<ProcessInfo, CapabilityLayerError> {
        self.context.require(Capability::ProcessList)?;
        Err(CapabilityLayerError::OsError("Process get not implemented".to_string()))
    }
    
    pub async fn kill(&mut self, pid: u32) -> Result<(), CapabilityLayerError> {
        self.context.require(Capability::ProcessKill)?;
        Err(CapabilityLayerError::OsError("Process kill not implemented".to_string()))
    }
    
    pub async fn start(&mut self, command: &str, args: &[&str]) -> Result<u32, CapabilityLayerError> {
        self.context.require(Capability::ProcessStart)?;
        Err(CapabilityLayerError::OsError("Process start not implemented".to_string()))
    }
    
    pub async fn execute(&mut self, command: &str) -> Result<String, CapabilityLayerError> {
        self.context.require(Capability::CommandExecute)?;
        Err(CapabilityLayerError::OsError("Command execution not implemented".to_string()))
    }
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct ProcessInfo {
    pub pid: u32,
    pub name: String,
    pub memory_usage: u64,
    pub cpu_usage: f32,
}

/// Service capability interface
pub struct ServiceCapability<'a> {
    context: &'a mut CapabilityContext,
}

impl<'a> ServiceCapability<'a> {
    pub async fn list(&mut self) -> Result<Vec<ServiceInfo>, CapabilityLayerError> {
        self.context.require(Capability::ServiceList)?;
        Err(CapabilityLayerError::OsError("Service list not implemented".to_string()))
    }
    
    pub async fn status(&mut self, service_name: &str) -> Result<ServiceInfo, CapabilityLayerError> {
        self.context.require(Capability::ServiceList)?;
        Err(CapabilityLayerError::OsError("Service status not implemented".to_string()))
    }
    
    pub async fn start(&mut self, service_name: &str) -> Result<(), CapabilityLayerError> {
        self.context.require(Capability::ServiceStart)?;
        Err(CapabilityLayerError::OsError("Service start not implemented".to_string()))
    }
    
    pub async fn stop(&mut self, service_name: &str) -> Result<(), CapabilityLayerError> {
        self.context.require(Capability::ServiceStop)?;
        Err(CapabilityLayerError::OsError("Service stop not implemented".to_string()))
    }
    
    pub async fn restart(&mut self, service_name: &str) -> Result<(), CapabilityLayerError> {
        self.context.require(Capability::ServiceRestart)?;
        
        self.stop(service_name).await?;
        tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
        self.start(service_name).await
    }
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct ServiceInfo {
    pub name: String,
    pub display_name: String,
    pub status: ServiceStatus,
    pub start_type: ServiceStartType,
}

#[derive(Debug, Clone, Copy, serde::Serialize, serde::Deserialize)]
pub enum ServiceStatus {
    Running,
    Stopped,
    Paused,
    StartPending,
    StopPending,
    ContinuePending,
    PausePending,
}

#[derive(Debug, Clone, Copy, serde::Serialize, serde::Deserialize)]
pub enum ServiceStartType {
    Boot,
    System,
    Automatic,
    Manual,
    Disabled,
}

/// System capability interface
pub struct SystemCapability<'a> {
    context: &'a mut CapabilityContext,
}

impl<'a> SystemCapability<'a> {
    pub async fn info(&mut self) -> Result<SystemInfo, CapabilityLayerError> {
        self.context.require(Capability::SystemInfo)?;
        Err(CapabilityLayerError::OsError("System info not implemented".to_string()))
    }
    
    pub async fn restart(&mut self) -> Result<(), CapabilityLayerError> {
        self.context.require(Capability::SystemRestart)?;
        Err(CapabilityLayerError::OsError("System restart not implemented".to_string()))
    }
    
    pub async fn shutdown(&mut self) -> Result<(), CapabilityLayerError> {
        self.context.require(Capability::SystemShutdown)?;
        Err(CapabilityLayerError::OsError("System shutdown not implemented".to_string()))
    }
    
    pub async fn sleep(&mut self) -> Result<(), CapabilityLayerError> {
        self.context.require(Capability::SystemSleep)?;
        Err(CapabilityLayerError::OsError("System sleep not implemented".to_string()))
    }
    
    pub async fn message(&mut self, title: &str, message: &str) -> Result<(), CapabilityLayerError> {
        self.context.require(Capability::DisplayMessage)?;
        Err(CapabilityLayerError::OsError("Display message not implemented".to_string()))
    }
    
    pub async fn notification(&mut self, title: &str, message: &str) -> Result<(), CapabilityLayerError> {
        self.context.require(Capability::DisplayNotification)?;
        Err(CapabilityLayerError::OsError("Notification not implemented".to_string()))
    }
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct SystemInfo {
    pub hostname: String,
    pub os_name: String,
    pub os_version: String,
    pub cpu_count: usize,
    pub total_memory: u64,
    pub used_memory: u64,
}

/// Path restriction check (sandbox)
fn is_path_allowed(path: &str) -> bool {
    let path_lower = path.to_lowercase();
    
    let blocked = [
        "windows\\system32",
        "program files",
        "program files (x86)",
        "users\\all users",
        "users\\default",
    ];
    
    for blocked_path in blocked {
        if path_lower.contains(blocked_path) {
            return false;
        }
    }
    
    true
}
