//! Aegis Cloud Windows Agent
//! 
//! Phase 1: Runs as a Windows Service (not just a desktop app)
//! - Auto-starts with Windows boot
//! - Runs even when no user is logged in
//! - Minimal CPU/RAM usage
//! - Auto-reconnect with exponential backoff
//! - Self-updating with signature verification

use std::sync::Arc;
use tokio::sync::RwLock;
use log::{info, error, warn};

mod ws;
mod tools;
mod system;
mod security;
mod service;
mod updater;
mod terminal;

mod queue;

use system::info::SystemInfo;

/// Agent configuration
#[derive(Clone)]
pub struct AgentConfig {
    pub server_url: String,
    pub device_token: Option<String>,
    pub pair_code: Option<String>,
    pub log_level: String,
    pub auto_update: bool,
    pub data_dir: String,
}

impl AgentConfig {
    pub fn from_env() -> Self {
        Self {
            server_url: std::env::var("AEGIS_SERVER_URL")
                .unwrap_or_else(|_| "wss://api.aegiscloud.in".to_string()),
            device_token: std::env::var("AEGIS_DEVICE_TOKEN").ok(),
            pair_code: std::env::var("AEGIS_PAIR_CODE").ok(),
            log_level: std::env::var("AEGIS_LOG_LEVEL")
                .unwrap_or_else(|_| "info".to_string()),
            auto_update: std::env::var("AEGIS_AUTO_UPDATE")
                .unwrap_or_else(|_| "true".to_string())
                .parse()
                .unwrap_or(true),
            data_dir: std::env::var("AEGIS_DATA_DIR")
                .unwrap_or_else(|_| {
                    std::path::PathBuf::from(std::env::var("ProgramData").unwrap_or_else(|_| "C:\\ProgramData".to_string()))
                        .join("AegisCloud")
                        .to_string_lossy()
                        .to_string()
                }),
        }
    }

    /// Ensure data directory exists
    pub fn ensure_dirs(&self) -> std::io::Result<()> {
        std::fs::create_dir_all(&self.data_dir)?;
        std::fs::create_dir_all(format!("{}/logs", self.data_dir))?;
        std::fs::create_dir_all(format!("{}/updates", self.data_dir))?;
        std::fs::create_dir_all(format!("{}/certs", self.data_dir))?;
        Ok(())
    }
}

/// Shared agent state
#[derive(Clone)]
pub struct AgentState {
    pub config: AgentConfig,
    pub device_token: Arc<RwLock<Option<String>>>,
    pub device_fingerprint: Arc<RwLock<Option<String>>>,
    pub connected: Arc<RwLock<bool>>,
    pub system_info: Arc<RwLock<SystemInfo>>,
    pub shutdown: Arc<RwLock<bool>>,
}

impl AgentState {
    pub fn new(config: AgentConfig) -> Self {
        Self {
            config,
            device_token: Arc::new(RwLock::new(None)),
            device_fingerprint: Arc::new(RwLock::new(None)),
            connected: Arc::new(RwLock::new(false)),
            system_info: Arc::new(RwLock::new(SystemInfo::gather())),
            shutdown: Arc::new(RwLock::new(false)),
        }
    }
}

/// Main agent loop — designed to be called from Windows Service
pub async fn run_agent(config: AgentConfig) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    info!("Aegis Cloud Agent v{} starting...", env!("CARGO_PKG_VERSION"));
    info!("Server: {}", config.server_url);
    info!("Auto-update: {}", config.auto_update);
    info!("Data dir: {}", config.data_dir);

    config.ensure_dirs()?;

    let state = AgentState::new(config.clone());

    // Load persisted device token
    if let Some(token) = &config.device_token {
        *state.device_token.write().await = Some(token.clone());
        info!("Device token loaded from config");
    } else {
        // Try to load from persistent storage
        let token_path = format!("{}/device_token", config.data_dir);
        if let Ok(token) = tokio::fs::read_to_string(&token_path).await {
            *state.device_token.write().await = Some(token.trim().to_string());
            info!("Device token loaded from persistent storage");
        }
    }

    // Generate device fingerprint if not exists
    {
        let fp = security::crypto::generate_device_fingerprint();
        *state.device_fingerprint.write().await = Some(fp.clone());
        info!("Device fingerprint: {}...", &fp[..16]);
    }

    // Start auto-updater in background (Phase 6)
    if config.auto_update {
        let updater_state = state.clone();
        tokio::spawn(async move {
            updater::run_update_loop(updater_state).await;
        });
    }

    // Main connection loop with exponential backoff
    let mut backoff = 1u64;
    let max_backoff = 300u64; // 5 minutes max

    loop {
        // Check for shutdown signal
        if *state.shutdown.read().await {
            info!("Shutdown signal received, exiting...");
            break;
        }

        let token = state.device_token.read().await.clone();
        if token.is_none() {
            info!("No device token. Waiting for pairing...");
            // In service mode, we'd wait for a pair code via named pipe or registry
            tokio::time::sleep(tokio::time::Duration::from_secs(10)).await;
            continue;
        }

        info!("Connecting to server...");
        match ws::client::connect_and_run(state.clone()).await {
            Ok(()) => {
                info!("Connection closed gracefully");
                backoff = 1;
            }
            Err(e) => {
                error!("Connection error: {}", e);
            }
        }

        *state.connected.write().await = false;

        info!("Reconnecting in {} seconds...", backoff);
        tokio::time::sleep(tokio::time::Duration::from_secs(backoff)).await;

        // Exponential backoff with jitter
        backoff = (backoff * 2).min(max_backoff);
        let jitter = rand::random::<u64>() % 5;
        backoff += jitter;
    }

    info!("Agent shutdown complete");
    Ok(())
}

#[tokio::main]
async fn main() {
    // Initialize logging
    env_logger::Builder::from_env(
        env_logger::Env::default().default_filter_or("info")
    ).init();

    info!("═══════════════════════════════════════════════");
    info!("  Aegis Cloud Agent v{}", env!("CARGO_PKG_VERSION"));
    info!("═══════════════════════════════════════════════");

    let config = AgentConfig::from_env();

    // Check if running as service or standalone
    let run_as_service = std::env::var("AEGIS_SERVICE_MODE")
        .unwrap_or_default()
        .parse::<bool>()
        .unwrap_or(false);

    if run_as_service {
        info!("Running as Windows Service...");
        match service::windows::run_as_service(config).await {
            Ok(()) => info!("Service exited normally"),
            Err(e) => error!("Service error: {}", e),
        }
    } else {
        info!("Running in standalone mode");
        match run_agent(config).await {
            Ok(()) => info!("Agent exited normally"),
            Err(e) => error!("Agent error: {}", e),
        }
    }
}
