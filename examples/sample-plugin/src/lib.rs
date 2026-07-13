//! Sample Aegis Cloud Plugin - System Diagnostics
//!
//! This plugin demonstrates the capability-based security model.

use aegis_plugin_runtime::prelude::*;
use aegis_plugin_sdk::tool;
use serde::{Deserialize, Serialize};

/// Get system uptime
#[tool(
    name = "get_uptime",
    description = "Get system uptime in human-readable format",
    category = "system",
    risk_level = "low",
    capabilities = ["system.info"]
)]
async fn get_uptime(ctx: &mut ToolContext) -> ToolResult {
    // This tool only needs system.info capability (low risk)
    // No special permissions required
    
    let sysinfo = sysinfo::System::new_all();
    let uptime = sysinfo.uptime();
    
    let days = uptime / 86400;
    let hours = (uptime % 86400) / 3600;
    let minutes = (uptime % 3600) / 60;
    
    let uptime_str = format!("{} days, {} hours, {} minutes", days, hours, minutes);
    
    Ok(ToolOutput::success(serde_json::json!({
        "uptime_seconds": uptime,
        "uptime_human": uptime_str
    })))
}

/// Get disk usage for a specific path
#[tool(
    name = "get_disk_usage",
    description = "Get disk usage statistics for a specific path",
    category = "system",
    risk_level = "low",
    capabilities = ["filesystem.read"]
)]
async fn get_disk_usage(ctx: &mut ToolContext, params: serde_json::Value) -> ToolResult {
    // This tool needs filesystem.read capability (low risk)
    
    #[derive(Deserialize)]
    struct DiskUsageParams {
        path: Option<String>,
    }
    
    let params: DiskUsageParams = serde_json::from_value(params)
        .map_err(|e| ToolError::InvalidParameters(e.to_string()))?;
    
    let path = params.path.unwrap_or_else(|| "C:\\".to_string());
    
    // Use the capability layer to check permissions
    let mut capabilities = ctx.capabilities();
    
    // This will fail if filesystem.read capability is not granted
    if !capabilities.filesystem().exists(&path).await.unwrap_or(false) {
        return Err(ToolError::NotFound(format!("Path not found: {}", path)));
    }
    
    // In production, use platform-specific disk APIs
    let total_gb = 500.0;
    let used_gb = 234.5;
    let free_gb = total_gb - used_gb;
    let percent_used = (used_gb / total_gb) * 100.0;
    
    Ok(ToolOutput::success(serde_json::json!({
        "path": path,
        "total_gb": total_gb,
        "used_gb": used_gb,
        "free_gb": free_gb,
        "percent_used": percent_used
    })))
}

/// List running services (requires approval)
#[tool(
    name = "list_services",
    description = "List all running Windows services",
    category = "system",
    risk_level = "medium",
    requires_approval = true,
    capabilities = ["service.list"]
)]
async fn list_services(ctx: &mut ToolContext) -> ToolResult {
    // This tool needs service.list capability (medium risk)
    // Requires admin approval before execution
    
    let mut capabilities = ctx.capabilities();
    
    // Use the capability layer to list services
    let services = capabilities.service().list().await
        .map_err(|e| ToolError::ExecutionFailed(e.to_string()))?;
    
    Ok(ToolOutput::success_with_message(
        &format!("Found {} services", services.len()),
        serde_json::json!({ "services": services })
    ))
}

/// Restart a Windows service (high risk)
#[tool(
    name = "restart_service",
    description = "Restart a Windows service by name",
    category = "system",
    risk_level = "high",
    requires_approval = true,
    capabilities = ["service.restart", "service.list"]
)]
async fn restart_service(ctx: &mut ToolContext, params: serde_json::Value) -> ToolResult {
    // This tool needs service.restart and service.list capabilities (high risk)
    // Requires admin approval
    
    #[derive(Deserialize)]
    struct RestartServiceParams {
        service_name: String,
    }
    
    let params: RestartServiceParams = serde_json::from_value(params)
        .map_err(|e| ToolError::InvalidParameters(e.to_string()))?;
    
    let mut capabilities = ctx.capabilities();
    
    // Check if service exists first
    let service = capabilities.service().status(&params.service_name).await
        .map_err(|e| ToolError::ExecutionFailed(e.to_string()))?;
    
    // Restart the service
    capabilities.service().restart(&params.service_name).await
        .map_err(|e| ToolError::ExecutionFailed(e.to_string()))?;
    
    Ok(ToolOutput::success(serde_json::json!({
        "service": params.service_name,
        "previous_status": format!("{:?}", service.status),
        "action": "restarted"
    })))
}

/// Find large files (requires filesystem access)
#[tool(
    name = "find_large_files",
    description = "Find files larger than a specified size",
    category = "file",
    risk_level = "low",
    capabilities = ["filesystem.read"]
)]
async fn find_large_files(ctx: &mut ToolContext, params: serde_json::Value) -> ToolResult {
    #[derive(Deserialize)]
    struct FindLargeFilesParams {
        path: Option<String>,
        min_size_mb: Option<u64>,
    }
    
    let params: FindLargeFilesParams = serde_json::from_value(params)
        .map_err(|e| ToolError::InvalidParameters(e.to_string()))?;
    
    let path = params.path.unwrap_or_else(|| "C:\\Users".to_string());
    let min_size_bytes = params.min_size_mb.unwrap_or(100) * 1024 * 1024;
    
    let mut capabilities = ctx.capabilities();
    
    // Use filesystem capability to search
    let mut large_files = Vec::new();
    
    fn search_dir(
        fs: &mut FileSystemCapability,
        path: &str,
        min_size: u64,
        results: &mut Vec<serde_json::Value>,
    ) -> Result<(), ToolError> {
        // This would recursively search directories
        // Using the filesystem.read capability
        Ok(())
    }
    
    // In production, this would walk the directory tree
    // For now, return a placeholder
    Ok(ToolOutput::success(serde_json::json!({
        "path": path,
        "min_size_mb": min_size_bytes / 1024 / 1024,
        "files_found": 0,
        "message": "File search completed"
    })))
}

/// Clean temporary files (requires write access)
#[tool(
    name = "clean_temp_files",
    description = "Clean temporary files from the system",
    category = "maintenance",
    risk_level = "medium",
    requires_approval = true,
    capabilities = ["filesystem.read", "filesystem.write.temp", "filesystem.delete"]
)]
async fn clean_temp_files(ctx: &mut ToolContext) -> ToolResult {
    // This tool needs multiple capabilities:
    // - filesystem.read (to list files)
    // - filesystem.write.temp (to write to temp)
    // - filesystem.delete (to delete files)
    
    let mut capabilities = ctx.capabilities();
    
    // Get temp directory
    let temp_dir = std::env::temp_dir();
    let temp_path = temp_dir.to_string_lossy();
    
    // Count files before cleanup
    let files_before = capabilities.filesystem().list_dir(&temp_path).await
        .map_err(|e| ToolError::ExecutionFailed(e.to_string()))?
        .len();
    
    // In production, this would delete temp files
    // using the filesystem.delete capability
    
    Ok(ToolOutput::success(serde_json::json!({
        "temp_directory": temp_path,
        "files_before": files_before,
        "files_deleted": 0,
        "space_freed_mb": 0,
        "message": "Cleanup completed"
    })))
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_get_uptime() {
        // Create a test context with system.info capability
        let mut granted = std::collections::HashSet::new();
        granted.insert(Capability::SystemInfo);
        
        let context = CapabilityContext::new(
            granted,
            "test-plugin".to_string(),
            "get_uptime".to_string()
        );
        
        let mut ctx = ToolContext::new(context);
        
        let result = get_uptime(&mut ctx).await;
        assert!(result.is_ok());
        
        let output = result.unwrap();
        assert!(output.success);
        assert!(output.data.get("uptime_seconds").is_some());
    }
    
    #[tokio::test]
    async fn test_get_disk_usage() {
        let mut granted = std::collections::HashSet::new();
        granted.insert(Capability::FilesystemRead);
        
        let context = CapabilityContext::new(
            granted,
            "test-plugin".to_string(),
            "get_disk_usage".to_string()
        );
        
        let mut ctx = ToolContext::new(context);
        
        let params = serde_json::json!({
            "path": "C:\\"
        });
        
        let result = get_disk_usage(&mut ctx, params).await;
        assert!(result.is_ok());
    }
}
