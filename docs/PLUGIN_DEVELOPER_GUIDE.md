# Aegis Cloud Plugin Developer Guide

Build powerful tools for Windows endpoint management with Rust.

## Quick Start

### 1. Install the CLI

```bash
cargo install aegis-cli
```

### 2. Create a New Plugin

```bash
aegis plugin init my-awesome-plugin
cd my-awesome-plugin
```

### 3. Write Your Tool

Edit `src/lib.rs`:

```rust
use aegis_plugin_runtime::prelude::*;
use aegis_plugin_sdk::tool;

#[tool(
    name = "get_cpu_temp",
    description = "Get CPU temperature",
    category = "system",
    risk_level = "low",
    timeout = 10
)]
async fn get_cpu_temp() -> ToolResult {
    // Your implementation here
    let temp = 45.5; // Read from hardware
    
    Ok(ToolOutput::success(serde_json::json!({
        "temperature_celsius": temp,
        "temperature_fahrenheit": temp * 9.0 / 5.0 + 32.0
    })))
}
```

### 4. Build and Publish

```bash
aegis plugin build --release
aegis plugin validate
aegis plugin publish
```

That's it! Your plugin is now available in the Aegis Cloud marketplace.

---

## Plugin Structure

```
my-plugin/
├── Cargo.toml          # Rust dependencies
├── manifest.json       # Plugin metadata
├── src/
│   └── lib.rs         # Your tools
├── tests/
│   └── test_my_tool.rs
└── README.md
```

### manifest.json

```json
{
  "name": "my-awesome-plugin",
  "version": "1.0.0",
  "author": "Your Name <you@example.com>",
  "description": "Awesome plugin that does cool stuff",
  "license": "MIT",
  "category": "system",
  "platform": "windows-x64",
  "homepage": "https://github.com/you/my-plugin",
  "repository": "https://github.com/you/my-plugin",
  "tools": [
    {
      "name": "get_cpu_temp",
      "description": "Get CPU temperature",
      "category": "system",
      "risk_level": "low",
      "requires_approval": false,
      "timeout": 10,
      "input_schema": {},
      "output_schema": {
        "type": "object",
        "properties": {
          "temperature_celsius": { "type": "number" },
          "temperature_fahrenheit": { "type": "number" }
        }
      }
    }
  ]
}
```

---

## The #[tool] Macro

The `#[tool]` macro generates all the boilerplate for tool registration, parameter validation, and marketplace listing.

### Required Attributes

- `name`: Tool name (snake_case, unique within plugin)
- `description`: Human-readable description
- `category`: Tool category
- `risk_level`: Security risk level
- `timeout`: Maximum execution time (seconds)

### Optional Attributes

- `requires_approval`: Requires admin approval (default: false)
- `input_schema`: JSON Schema for parameters
- `output_schema`: JSON Schema for output

### Categories

- `system`: System information and utilities
- `process`: Process management
- `file`: File operations
- `network`: Network utilities
- `security`: Security tools
- `maintenance`: System maintenance
- `diagnostic`: Diagnostic tools
- `monitoring`: Monitoring tools
- `custom`: Custom tools

### Risk Levels

- `low`: Read-only operations, no system changes
- `medium`: Modifies system settings, requires caution
- `high`: Significant system changes, requires approval
- `critical`: Dangerous operations, requires explicit admin approval

---

## Tool Parameters

### No Parameters

```rust
#[tool(
    name = "list_services",
    description = "List all Windows services",
    category = "system",
    risk_level = "low"
)]
async fn list_services() -> ToolResult {
    let services = get_services()?;
    
    Ok(ToolOutput::success(serde_json::json!({
        "services": services
    })))
}
```

### With Parameters

```rust
use serde::Deserialize;

#[derive(Deserialize)]
struct KillProcessParams {
    pid: u32,
    force: Option<bool>,
}

#[tool(
    name = "kill_process",
    description = "Kill a process by PID",
    category = "process",
    risk_level = "high",
    requires_approval = true
)]
async fn kill_process(params: serde_json::Value) -> ToolResult {
    let params: KillProcessParams = serde_json::from_value(params)
        .map_err(|e| ToolError::InvalidParameters(e.to_string()))?;
    
    let force = params.force.unwrap_or(false);
    
    // Kill the process
    kill_process_by_pid(params.pid, force)?;
    
    Ok(ToolOutput::success(serde_json::json!({
        "killed_pid": params.pid,
        "force": force
    })))
}
```

---

## Error Handling

Return errors using `ToolError`:

```rust
async fn my_tool() -> ToolResult {
    match do_something() {
        Ok(result) => Ok(ToolOutput::success(result)),
        Err(e) => Err(ToolError::ExecutionFailed(e.to_string())),
    }
}
```

### Error Types

- `InvalidParameters`: Invalid input parameters
- `ExecutionFailed`: Tool execution failed
- `PermissionDenied`: Insufficient permissions
- `NotFound`: Resource not found
- `Timeout`: Execution timed out
- `Internal`: Internal error

---

## Testing

Test your tools locally before publishing:

```bash
cargo test
```

Example test:

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_get_cpu_temp() {
        let result = get_cpu_temp().await;
        assert!(result.is_ok());
        
        let output = result.unwrap();
        assert!(output.success);
        assert!(output.data.get("temperature_celsius").is_some());
    }
}
```

---

## Publishing

### 1. Validate

```bash
aegis plugin validate
```

Checks:
- Manifest format
- Tool definitions
- Binary size
- Dangerous patterns
- Security requirements

### 2. Build

```bash
aegis plugin build --release
```

### 3. Publish

```bash
aegis plugin publish
```

Requirements:
- Valid API key (from https://cloud.aegis.io/settings/api)
- Plugin passes validation
- Binary is signed

---

## Security

### Sandboxing

All plugins run in a sandbox with:
- Limited filesystem access
- No network access (unless explicitly granted)
- Memory limits (100MB default)
- Execution time limits

### Dangerous Operations

These operations are **blocked**:
- `rm -rf` / recursive delete
- Format drives
- Disable firewall
- Stop critical services
- Modify registry without approval
- Execute arbitrary commands

### Approval Workflow

Tools with `risk_level: "high"` or `critical` require admin approval:

1. User requests tool execution
2. System sends approval request to admin
3. Admin reviews and approves/rejects
4. Tool executes if approved

---

## Examples

### System Information

```rust
#[tool(
    name = "get_system_info",
    description = "Get comprehensive system information",
    category = "system",
    risk_level = "low"
)]
async fn get_system_info() -> ToolResult {
    let info = serde_json::json!({
        "hostname": whoami::hostname(),
        "username": whoami::username(),
        "os": std::env::consts::OS,
        "arch": std::env::consts::ARCH,
        "cpu_count": num_cpus::get(),
        "memory_total": sys_info::mem_info().map(|m| m.total).unwrap_or(0),
    });
    
    Ok(ToolOutput::success(info))
}
```

### File Operations

```rust
use serde::Deserialize;

#[derive(Deserialize)]
struct FileSearchParams {
    pattern: String,
    path: Option<String>,
}

#[tool(
    name = "find_large_files",
    description = "Find files larger than a specified size",
    category = "file",
    risk_level = "low"
)]
async fn find_large_files(params: serde_json::Value) -> ToolResult {
    let params: FileSearchParams = serde_json::from_value(params)?;
    let search_path = params.path.unwrap_or_else(|| ".".to_string());
    
    let mut large_files = Vec::new();
    
    for entry in walkdir::WalkDir::new(&search_path) {
        let entry = entry?;
        if entry.file_type().is_file() {
            let metadata = entry.metadata()?;
            if metadata.len() > 100 * 1024 * 1024 { // > 100MB
                large_files.push(serde_json::json!({
                    "path": entry.path().to_string_lossy(),
                    "size_mb": metadata.len() / 1024 / 1024,
                }));
            }
        }
    }
    
    Ok(ToolOutput::success(serde_json::json!({
        "files": large_files,
        "count": large_files.len()
    })))
}
```

### Network Diagnostics

```rust
#[tool(
    name = "ping_host",
    description = "Ping a remote host",
    category = "network",
    risk_level = "low"
)]
async fn ping_host(params: serde_json::Value) -> ToolResult {
    let host = params["host"].as_str()
        .ok_or_else(|| ToolError::InvalidParameters("Missing host".to_string()))?;
    
    let output = tokio::process::Command::new("ping")
        .args(["-n", "4", host])
        .output()
        .await?;
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    
    Ok(ToolOutput::success(serde_json::json!({
        "host": host,
        "output": stdout,
        "success": output.status.success()
    })))
}
```

---

## Best Practices

### 1. Validate Input Early

```rust
async fn my_tool(params: serde_json::Value) -> ToolResult {
    let params: MyParams = serde_json::from_value(params)
        .map_err(|e| ToolError::InvalidParameters(e.to_string()))?;
    
    if params.value.is_empty() {
        return Err(ToolError::InvalidParameters("Value cannot be empty".to_string()));
    }
    
    // ... rest of implementation
}
```

### 2. Provide Detailed Output

```rust
Ok(ToolOutput::success(serde_json::json!({
    "status": "success",
    "details": {
        "processed": 42,
        "skipped": 3,
        "errors": 0
    },
    "message": "Successfully processed 42 items"
})))
```

### 3. Handle Errors Gracefully

```rust
async fn my_tool() -> ToolResult {
    match risky_operation() {
        Ok(result) => Ok(ToolOutput::success(result)),
        Err(e) => {
            log::error!("Operation failed: {}", e);
            Err(ToolError::ExecutionFailed(e.to_string()))
        }
    }
}
```

### 4. Document Your Tools

Add comprehensive descriptions and examples in your manifest:

```json
{
  "name": "my_tool",
  "description": "Does something useful. Example: my_tool(value=42) returns result.",
  "category": "system",
  "risk_level": "low"
}
```

### 5. Test Edge Cases

```rust
#[tokio::test]
async fn test_empty_input() {
    let result = my_tool(serde_json::json!({})).await;
    assert!(result.is_err());
}

#[tokio::test]
async fn test_invalid_input() {
    let result = my_tool(serde_json::json!({"value": "not_a_number"})).await;
    assert!(result.is_err());
}
```

---

## API Reference

### ToolOutput

```rust
pub struct ToolOutput {
    pub success: bool,
    pub message: String,
    pub data: serde_json::Value,
    pub duration_ms: Option<u64>,
}

impl ToolOutput {
    pub fn success<T: Serialize>(data: T) -> Self
    pub fn success_with_message<T: Serialize>(message: &str, data: T) -> Self
}
```

### ToolError

```rust
pub enum ToolError {
    InvalidParameters(String),
    ExecutionFailed(String),
    PermissionDenied(String),
    NotFound(String),
    Timeout(u32),
    Internal(String),
}
```

---

## Marketplace

Your plugin appears in the marketplace at:

```
https://marketplace.aegiscloud.io/plugins/{your-plugin-id}
```

Users can:
- Browse your plugin
- View documentation
- Install with one click
- Rate and review
- Report issues

---

## Support

- Documentation: https://docs.aegiscloud.io/plugins
- Discord: https://discord.gg/aegiscloud
- GitHub: https://github.com/aegis-cloud/plugin-sdk
- Email: plugins@aegiscloud.io

---

## License

The Aegis Plugin SDK is MIT licensed. Your plugins can use any license you choose.

---

**Ready to build something awesome? Start with `aegis plugin init`!**
