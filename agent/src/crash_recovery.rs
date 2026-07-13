//! Crash Recovery — Survive reboots, sleep, crashes, network loss
//!
//! The agent must be bulletproof:
//! - Survive Windows reboots (Windows Service auto-restart)
//! - Survive sleep/hibernate (reconnect on wake)
//! - Survive VPN/WiFi changes (detect and reconnect)
//! - Survive Windows Update (agent survives update reboots)
//! - Survive crashes (restart with backoff)
//! - Persist state to disk (resume where left off)
//! - Corrupted state recovery (detect and reset)

use std::path::PathBuf;
use std::sync::Arc;
use tokio::sync::RwLock;
use serde::{Deserialize, Serialize};
use log::{info, warn, error};
use chrono::{DateTime, Utc};

/// Persisted agent state — survives crashes and reboots
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PersistedState {
    /// Agent version at last checkpoint
    pub agent_version: String,
    /// Last known good timestamp
    pub last_checkpoint: DateTime<Utc>,
    /// Number of consecutive failures
    pub failure_count: u32,
    /// Commands in-flight when crash happened
    pub in_flight_commands: Vec<String>,
    /// Whether a clean shutdown was performed
    pub clean_shutdown: bool,
    /// Last successful heartbeat
    pub last_heartbeat: Option<DateTime<Utc>>,
    /// Device token (encrypted)
    pub device_token: Option<String>,
    /// Device fingerprint
    pub device_fingerprint: Option<String>,
    /// Current WebSocket connection ID
    pub connection_id: Option<String>,
    /// Number of crash restarts today
    pub restarts_today: u32,
    /// Date of restart counter reset
    pub restart_date: String,
}

impl PersistedState {
    pub fn new(agent_version: String) -> Self {
        let today = Utc::now().format("%Y-%m-%d").to_string();
        Self {
            agent_version,
            last_checkpoint: Utc::now(),
            failure_count: 0,
            in_flight_commands: Vec::new(),
            clean_shutdown: false,
            last_heartbeat: None,
            device_token: None,
            device_fingerprint: None,
            connection_id: None,
            restarts_today: 0,
            restart_date: today,
        }
    }
}

/// Crash recovery manager
pub struct CrashRecovery {
    data_dir: PathBuf,
    state: Arc<RwLock<PersistedState>>,
}

impl CrashRecovery {
    pub fn new(data_dir: String) -> Self {
        Self {
            data_dir: PathBuf::from(data_dir),
            state: Arc::new(RwLock::new(PersistedState::new(
                env!("CARGO_PKG_VERSION").to_string()
            ))),
        }
    }

    /// Load persisted state from disk, or create fresh
    pub async fn load_or_create(&self) -> Result<PersistedState, Box<dyn std::error::Error + Send + Sync>> {
        let state_path = self.data_dir.join("agent_state.json");
        
        if state_path.exists() {
            match tokio::fs::read_to_string(&state_path).await {
                Ok(content) => {
                    match serde_json::from_str::<PersistedState>(&content) {
                        Ok(mut state) => {
                            // Check if this was a clean shutdown
                            if !state.clean_shutdown {
                                warn!("Detected unclean shutdown — recovering state");
                                state.failure_count += 1;
                                state.restarts_today += 1;
                                
                                // Reset daily counter if new day
                                let today = Utc::now().format("%Y-%m-%d").to_string();
                                if state.restart_date != today {
                                    state.restarts_today = 1;
                                    state.restart_date = today;
                                }
                                
                                // Check for crash loop (5+ restarts today)
                                if state.restarts_today > 5 {
                                    error!("Crash loop detected! {} restarts today. Backing off...", 
                                           state.restarts_today);
                                    // Signal to main loop to wait longer
                                    tokio::time::sleep(tokio::time::Duration::from_secs(600)).await;
                                }
                                
                                // Mark in-flight commands as failed
                                if !state.in_flight_commands.is_empty() {
                                    warn!("{} commands were in-flight during crash", 
                                          state.in_flight_commands.len());
                                    // These will be reported as failed on next connection
                                }
                            }
                            
                            // Mark as not clean shutdown until we shut down cleanly
                            state.clean_shutdown = false;
                            
                            *self.state.write().await = state.clone();
                            info!("State loaded from disk");
                            return Ok(state);
                        }
                        Err(e) => {
                            error!("Corrupted state file: {}. Starting fresh.", e);
                        }
                    }
                }
                Err(e) => {
                    error!("Failed to read state file: {}. Starting fresh.", e);
                }
            }
        }
        
        // No existing state or corrupted — create fresh
        let state = PersistedState::new(env!("CARGO_PKG_VERSION").to_string());
        self.save_state(&state).await?;
        info!("Created fresh state");
        Ok(state)
    }

    /// Save state to disk atomically
    pub async fn save_state(&self, state: &PersistedState) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let state_path = self.data_dir.join("agent_state.json");
        let tmp_path = self.data_dir.join("agent_state.json.tmp");
        
        let content = serde_json::to_string_pretty(state)?;
        
        // Write to temp file first, then rename (atomic on Windows)
        tokio::fs::write(&tmp_path, &content).await?;
        tokio::fs::rename(&tmp_path, &state_path).await?;
        
        Ok(())
    }

    /// Record a successful checkpoint
    pub async fn record_checkpoint(&self) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let mut state = self.state.write().await;
        state.last_checkpoint = Utc::now();
        state.failure_count = 0;
        self.save_state(&state).await?;
        Ok(())
    }

    /// Record agent start
    pub async fn record_start(&self) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let state = self.state.read().await;
        info!("Agent started. Failure count: {}, Restarts today: {}", 
              state.failure_count, state.restarts_today);
        Ok(())
    }

    /// Record successful heartbeat
    pub async fn record_heartbeat(&self) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let mut state = self.state.write().await;
        state.last_heartbeat = Some(Utc::now());
        self.save_state(&state).await?;
        Ok(())
    }

    /// Record command in-flight (for crash recovery)
    pub async fn record_command_start(&self, command_id: &str) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let mut state = self.state.write().await;
        if !state.in_flight_commands.contains(&command_id.to_string()) {
            state.in_flight_commands.push(command_id.to_string());
            self.save_state(&state).await?;
        }
        Ok(())
    }

    /// Remove command from in-flight list
    pub async fn record_command_complete(&self, command_id: &str) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let mut state = self.state.write().await;
        state.in_flight_commands.retain(|id| id != command_id);
        self.save_state(&state).await?;
        Ok(())
    }

    /// Get in-flight commands (for reporting after crash)
    pub async fn get_in_flight_commands(&self) -> Vec<String> {
        self.state.read().await.in_flight_commands.clone()
    }

    /// Record clean shutdown
    pub async fn record_shutdown(&self) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let mut state = self.state.write().await;
        state.clean_shutdown = true;
        state.in_flight_commands.clear();
        self.save_state(&state).await?;
        info!("Clean shutdown recorded");
        Ok(())
    }

    /// Store device token persistently
    pub async fn store_device_token(&self, token: &str) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let mut state = self.state.write().await;
        state.device_token = Some(token.to_string());
        self.save_state(&state).await?;
        Ok(())
    }

    /// Get persisted device token
    pub async fn get_device_token(&self) -> Option<String> {
        self.state.read().await.device_token.clone()
    }

    /// Get current state
    pub async fn get_state(&self) -> PersistedState {
        self.state.read().await.clone()
    }

    /// Check if we should back off due to too many failures
    pub async fn should_backoff(&self) -> Option<u64> {
        let state = self.state.read().await;
        
        if state.restarts_today > 10 {
            // Too many restarts — back off for 10 minutes
            Some(600)
        } else if state.restarts_today > 5 {
            // Several restarts — back off for 2 minutes
            Some(120)
        } else if state.failure_count > 3 {
            // A few failures — back off for 30 seconds
            Some(30)
        } else {
            None
        }
    }
}
