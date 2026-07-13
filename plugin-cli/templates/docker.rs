//! Docker Management Plugin Template

use aegis_plugin_runtime::prelude::*;
use aegis_plugin_sdk::tool;
use serde::Deserialize;

#[tool(
    name = "docker_ps",
    description = "List running Docker containers",
    category = "system",
    risk_level = "low",
    timeout = 30
)]
async fn docker_ps() -> ToolResult {
    let output = tokio::process::Command::new("docker")
        .args(["ps", "--format", "{{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}"])
        .output()
        .await
        .map_err(|e| ToolError::ExecutionFailed(e.to_string()))?;
    
    if !output.status.success() {
        return Err(ToolError::ExecutionFailed(
            String::from_utf8_lossy(&output.stderr).to_string(),
        ));
    }
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    let containers: Vec<serde_json::Value> = stdout
        .lines()
        .filter(|line| !line.is_empty())
        .map(|line| {
            let parts: Vec<&str> = line.split('\t').collect();
            serde_json::json!({
                "id": parts.get(0).unwrap_or(&""),
                "name": parts.get(1).unwrap_or(&""),
                "status": parts.get(2).unwrap_or(&""),
                "image": parts.get(3).unwrap_or(&"")
            })
        })
        .collect();
    
    Ok(ToolOutput::success(serde_json::json!({
        "containers": containers
    })))
}

#[derive(Deserialize)]
struct ContainerIdParams {
    container_id: String,
}

#[tool(
    name = "docker_stop",
    description = "Stop a Docker container",
    category = "system",
    risk_level = "medium",
    requires_approval = true,
    timeout = 60
)]
async fn docker_stop(params: serde_json::Value) -> ToolResult {
    let params: ContainerIdParams = serde_json::from_value(params)
        .map_err(|e| ToolError::InvalidParameters(e.to_string()))?;
    
    let output = tokio::process::Command::new("docker")
        .args(["stop", &params.container_id])
        .output()
        .await
        .map_err(|e| ToolError::ExecutionFailed(e.to_string()))?;
    
    if !output.status.success() {
        return Err(ToolError::ExecutionFailed(
            String::from_utf8_lossy(&output.stderr).to_string(),
        ));
    }
    
    Ok(ToolOutput::success(serde_json::json!({
        "stopped": params.container_id
    })))
}
