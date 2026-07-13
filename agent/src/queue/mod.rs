//! Command Queue - Manages command lifecycle on the agent side.
//!
//! Phase 3: Commands go through proper states:
//!   queued → executing → completed
//!                       → failed
//!
//! Every command has:
//! - Unique ID
//! - Nonce (replay protection)
//! - Timeout
//! - Progress updates
//! - Structured result

use std::collections::VecDeque;
use std::sync::Arc;
use tokio::sync::{Mutex, RwLock};
use serde::{Deserialize, Serialize};
use log::{info, error};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueuedCommand {
    pub id: String,
    pub tool_name: String,
    pub parameters: serde_json::Value,
    pub nonce: String,
    pub priority: u8,
    pub timeout_seconds: u32,
    pub status: CommandState,
    pub progress: u8,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum CommandState {
    Queued,
    Executing,
    Completed,
    Failed,
    Cancelled,
    Timeout,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CommandResult {
    pub command_id: String,
    pub status: CommandState,
    pub progress: u8,
    pub result: Option<serde_json::Value>,
    pub error: Option<String>,
    pub logs: Vec<String>,
}

/// Agent-side command queue
pub struct CommandQueue {
    queue: Arc<Mutex<VecDeque<QueuedCommand>>>,
    executed: Arc<Mutex<Vec<CommandResult>>>,
    nonces: Arc<RwLock<Vec<String>>>,  // Replay protection
}

impl CommandQueue {
    pub fn new() -> Self {
        Self {
            queue: Arc::new(Mutex::new(VecDeque::new())),
            executed: Arc::new(Mutex::new(Vec::new())),
            nonces: Arc::new(RwLock::new(Vec::new())),
        }
    }

    /// Add a command to the queue with replay protection
    pub async fn enqueue(&self, cmd: QueuedCommand) -> Result<(), String> {
        // Phase 5: Replay protection — check nonce hasn't been used
        let nonces = self.nonces.read().await;
        if nonces.contains(&cmd.nonce) {
            return Err(format!("Replay detected: nonce {} already used", cmd.nonce));
        }
        drop(nonces);

        // Store nonce
        let mut nonces = self.nonces.write().await;
        nonces.push(cmd.nonce.clone());

        // Keep nonce history bounded (last 10,000)
        if nonces.len() > 10_000 {
            let drain_count = nonces.len() - 10_000;
            nonces.drain(..drain_count);
        }
        drop(nonces);

        // Add to queue sorted by priority
        let mut queue = self.queue.lock().await;
        let pos = queue.iter().position(|c| c.priority < cmd.priority).unwrap_or(queue.len());
        queue.insert(pos, cmd);

        info!("Command queued: {}", cmd.id);
        Ok(())
    }

    /// Get the next command to execute
    pub async fn dequeue(&self) -> Option<QueuedCommand> {
        let mut queue = self.queue.lock().await;
        queue.pop_front()
    }

    /// Record command result
    pub async fn record_result(&self, result: CommandResult) {
        let mut executed = self.executed.lock().await;
        executed.push(result);

        // Keep history bounded
        if executed.len() > 1000 {
            executed.drain(..executed.len() - 1000);
        }
    }

    /// Get pending command count
    pub async fn pending_count(&self) -> usize {
        self.queue.lock().await.len()
    }

    /// Cancel a queued command
    pub async fn cancel(&self, command_id: &str) -> bool {
        let mut queue = self.queue.lock().await;
        if let Some(pos) = queue.iter().position(|c| c.id == command_id) {
            queue.remove(pos);
            info!("Command cancelled: {}", command_id);
            true
        } else {
            false
        }
    }
}
