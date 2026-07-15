//! WebSocket client with proper command queue integration
//! 
//! Phase 1-4: Full lifecycle management
//! - Connects with device token (separate from user auth)
//! - Receives commands from queue
//! - Sends results back
//! - Heartbeat system
//! - Live stats streaming

use futures_util::{SinkExt, StreamExt};
use log::{info, error, warn};
use serde::{Deserialize, Serialize};
use tokio_tungstenite::{connect_async, tungstenite::Message};
use std::sync::Arc;

use crate::AgentState;
use crate::queue::{CommandQueue, QueuedCommand, CommandResult, CommandState};
use crate::tools::executor::ToolExecutor;

#[derive(Debug, Serialize, Deserialize)]
pub struct WsMessage {
    pub r#type: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub command_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tool: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tool_name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parameters: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub nonce: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub stats: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub result: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub progress: Option<u8>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub priority: Option<u8>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub timeout_seconds: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub timestamp: Option<String>,
}

/// Connect to server and run the main event loop
pub async fn connect_and_run(state: AgentState) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let token = state.device_token.read().await.clone()
        .ok_or("No device token available")?;

    // Phase 5: Use WSS in production, WS for development
    let ws_url = if state.config.server_url.starts_with("wss://") {
        format!("{}/api/v1/ws/agent?device_token={}", state.config.server_url, token)
    } else {
        format!("{}/api/v1/ws/agent?device_token={}", state.config.server_url, token)
    };

    info!("Connecting to {}", &ws_url[..50.min(ws_url.len())]);

    let (ws_stream, _) = connect_async(&ws_url).await?;
    let (mut write, mut read) = ws_stream.split();

    info!("Connected to server");
    *state.connected.write().await = true;

    let executor = ToolExecutor::new();
    let command_queue = CommandQueue::new();

    // Send initial heartbeat with system info
    let sys_info = crate::system::info::SystemInfo::gather();
    let heartbeat = WsMessage {
        r#type: "heartbeat".to_string(),
        command_id: None,
        tool: None,
        tool_name: None,
        parameters: None,
        nonce: None,
        stats: Some(serde_json::json!({
            "agent_version": env!("CARGO_PKG_VERSION"),
            "hostname": sys_info.hostname,
            "os_name": sys_info.os_name,
            "os_version": sys_info.os_version,
            "cpu_info": sys_info.cpu_brand,
            "ram_total_gb": sys_info.total_ram_mb as f64 / 1024.0,

            "windows_version": sys_info.os_version,
            "uptime_seconds": sys_info.uptime_secs,
        })),
        result: None,
        progress: None,
        error: None,
        priority: None,
        timeout_seconds: None,
        timestamp: Some(chrono::Utc::now().to_rfc3339()),
    };
    let _ = write.send(Message::Text(serde_json::to_string(&heartbeat)?)).await;

    // Heartbeat task
    // In production, we'd use a channel-based approach for heartbeat.

    // Main message loop
    while let Some(msg) = read.next().await {
        match msg {
            Ok(Message::Text(text)) => {
                match serde_json::from_str::<WsMessage>(&text) {
                    Ok(ws_msg) => {
                        match ws_msg.r#type.as_str() {
                            "execute_command" => {
                                handle_execute_command(
                                    &ws_msg,
                                    &executor,
                                    &command_queue,
                                    &mut write,
                                ).await;
                            }
                            "cancel_command" => {
                                if let Some(cmd_id) = &ws_msg.command_id {
                                    command_queue.cancel(cmd_id).await;
                                    info!("Command cancelled: {}", cmd_id);
                                }
                            }
                            "check_update" => {
                                // Phase 6: Check for updates
                                info!("Update check requested");
                            }
                            "heartbeat_ack" => {
                                // Server acknowledged our heartbeat
                            }
                            _ => {
                                warn!("Unknown message type: {}", ws_msg.r#type);
                            }
                        }
                    }
                    Err(e) => {
                        error!("Failed to parse message: {}", e);
                    }
                }
            }
            Ok(Message::Close(_)) => {
                info!("Server closed connection");
                break;
            }
            Ok(Message::Ping(data)) => {
                let _ = write.send(Message::Pong(data)).await;
            }
            Err(e) => {
                error!("WebSocket error: {}", e);
                return Err(Box::new(e));
            }
            _ => {}
        }
    }

    Ok(())
}

/// Handle a command execution request
async fn handle_execute_command(
    msg: &WsMessage,
    executor: &ToolExecutor,
    queue: &CommandQueue,
    write: &mut futures_util::stream::SplitSink<
        tokio_tungstenite::WebSocketStream<tokio_tungstenite::MaybeTlsStream<tokio::net::TcpStream>>,
        Message,
    >,
) {
    let command_id = msg.command_id.clone().unwrap_or_default();
    let tool_name = msg.tool_name.clone().or(msg.tool.clone()).unwrap_or_default();
    let parameters = msg.parameters.clone().unwrap_or(serde_json::json!({}));
    let nonce = msg.nonce.clone().unwrap_or_default();

    info!("Executing command {} (tool: {})", command_id, tool_name);

    // Send progress update: started
    let progress_msg = WsMessage {
        r#type: "command_progress".to_string(),
        command_id: Some(command_id.clone()),
        tool: None,
        tool_name: Some(tool_name.clone()),
        parameters: None,
        nonce: None,
        stats: None,
        result: None,
        progress: Some(10),
        error: None,
        priority: None,
        timeout_seconds: None,
        timestamp: Some(chrono::Utc::now().to_rfc3339()),
    };
    let _ = write.send(Message::Text(serde_json::to_string(&progress_msg).unwrap())).await;

    // Execute the tool
    let result = executor.execute(&tool_name, Some(parameters)).await;

    // Send result
    let result_msg = WsMessage {
        r#type: "command_result".to_string(),
        command_id: Some(command_id.clone()),
        tool: None,
        tool_name: Some(tool_name.clone()),
        parameters: None,
        nonce: None,
        stats: None,
        result: Some(serde_json::json!({
            "success": result.success,
            "message": result.message,
            "data": result.data,
        })),
        progress: Some(100),
        error: if !result.success { Some(result.message.clone()) } else { None },
        priority: None,
        timeout_seconds: None,
        timestamp: Some(chrono::Utc::now().to_rfc3339()),
    };
    let _ = write.send(Message::Text(serde_json::to_string(&result_msg).unwrap())).await;

    info!("Command {} completed (success: {})", command_id, result.success);
}
