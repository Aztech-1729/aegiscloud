//! Basic Plugin Template

use aegis_plugin_runtime::prelude::*;
use aegis_plugin_sdk::tool;

#[tool(
    name = "hello_world",
    description = "A simple hello world tool",
    category = "custom",
    risk_level = "low",
    timeout = 10
)]
async fn hello_world() -> ToolResult {
    Ok(ToolOutput::success(serde_json::json!({
        "message": "Hello from Aegis Cloud Plugin!"
    })))
}
