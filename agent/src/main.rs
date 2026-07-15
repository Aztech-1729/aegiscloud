//! Aegis Cloud Windows Agent
//! 
//! Phase 1: Runs as a Windows Service (not just a desktop app)
//! - Auto-starts with Windows boot
//! - Runs even when no user is logged in
//! - Minimal CPU/RAM usage
//! - Auto-reconnect with exponential backoff
//! - Self-updating with signature verification

use std::io::{self, Write};
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


/// Try to pair with the server using a pair code
async fn try_pair(
    server_url: &str,
    pair_code: &str,
    data_dir: &str,
) -> Result<(String, String, String), Box<dyn std::error::Error + Send + Sync>> {
    let http_url = server_url
        .replace("wss://", "https://")
        .replace("ws://", "http://");

    let hostname = hostname::get()
        .map(|h| h.to_string_lossy().to_string())
        .unwrap_or_else(|_| "Unknown".to_string());

    let os_info = format!("Windows {}", std::env::var("OS").unwrap_or_else(|_| "Unknown".to_string()));

    let body = serde_json::json!({
        "pair_code": pair_code,
        "hostname": hostname,
        "os_info": os_info,
    });

    let client = reqwest::Client::new();
    let resp = client
        .post(format!("{}/api/v1/devices/pair-agent", http_url))
        .json(&body)
        .send()
        .await?;

    let status = resp.status();
    let text = resp.text().await?;

    if !status.is_success() {
        return Err(format!("Pairing failed ({}): {}", status, text).into());
    }

    let data: serde_json::Value = serde_json::from_str(&text)?;
    let device_id = data["device_id"].as_str().unwrap_or("").to_string();
    let device_token = data["device_token"].as_str().unwrap_or("").to_string();
    let device_name = data["device_name"].as_str().unwrap_or("Unknown").to_string();

    Ok((device_id, device_token, device_name))
}

/// Main agent loop — interactive mode for standalone, event loop for service
pub async fn run_agent(config: AgentConfig) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    config.ensure_dirs()?;

    let state = AgentState::new(config.clone());

    // Load persisted device token
    if let Some(token) = &config.device_token {
        *state.device_token.write().await = Some(token.clone());
    } else {
        let token_path = format!("{}/device_token", config.data_dir);
        if let Ok(token) = tokio::fs::read_to_string(&token_path).await {
            let token = token.trim().to_string();
            if !token.is_empty() {
                *state.device_token.write().await = Some(token);
            }
        }
    }

    // Generate device fingerprint
    {
        let fp = security::crypto::generate_device_fingerprint();
        *state.device_fingerprint.write().await = Some(fp.clone());
    }

    let is_paired = state.device_token.read().await.is_some();

    if is_paired {
        // Already paired — connect directly
        print_banner(true);
        println!("  Status:    {}Connected{}", color("green"), color("reset"));
        println!("  Server:    {}", config.server_url);
        println!("{}", "─".repeat(45));
        println!();
    } else {
        // Need pairing
        print_banner(false);
        println!("  Status:    {}Not Paired{}", color("yellow"), color("reset"));
        println!("  Server:    {}", config.server_url);
        println!("{}", "─".repeat(45));
        println!();
        println!("  {}How to pair:{}", color("bold"), color("reset"));
        println!("  1. Go to {}", color("cyan"));
        println!("     https://aegiscloud.in/dashboard/devices");
        println!("  2. Click {}Generate Pair Code{}", color("bold"), color("reset"));
        println!("  3. Enter the code below");
        println!();

        // Interactive pairing loop
        let paired = interactive_pair(&config, &state).await?;
        if !paired {
            return Ok(());
        }

        println!();
        println!("  {}Connected!{}", color("green"), color("reset"));
        println!("  Device: {}{}{}", color("cyan"), 
            state.device_token.read().await.as_deref().unwrap_or(""),
            color("reset"));
        println!();
    }

    // Start auto-updater in background
    if config.auto_update {
        let updater_state = state.clone();
        tokio::spawn(async move {
            updater::run_update_loop(updater_state).await;
        });
    }

    // Main connection loop
    let mut backoff = 1u64;
    let max_backoff = 300u64;

    loop {
        if *state.shutdown.read().await {
            break;
        }

        let token = state.device_token.read().await.clone();
        if token.is_none() {
            println!("  {}Disconnected{}", color("red"), color("reset"));
            println!("  Run the agent again to reconnect.");
            break;
        }

        println!("  {}Connecting...{}", color("yellow"), color("reset"));
        match ws::client::connect_and_run(state.clone()).await {
            Ok(()) => {
                println!("  {}Connection closed{}", color("yellow"), color("reset"));
                backoff = 1;
            }
            Err(e) => {
                error!("Connection error: {}", e);
            }
        }

        *state.connected.write().await = false;

        println!("  Reconnecting in {}s...", backoff);
        tokio::time::sleep(tokio::time::Duration::from_secs(backoff)).await;

        backoff = (backoff * 2).min(max_backoff);
        let jitter = rand::random::<u64>() % 5;
        backoff += jitter;
    }

    Ok(())
}

/// Interactive pairing — prompts user for code
async fn interactive_pair(
    config: &AgentConfig,
    state: &AgentState,
) -> Result<bool, Box<dyn std::error::Error + Send + Sync>> {
    loop {
        print!("  {}Enter pairing code: {}", color("bold"), color("reset"));
        io::stdout().flush()?;

        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        let code = input.trim().to_string();

        if code.is_empty() {
            continue;
        }
        if code.eq_ignore_ascii_case("quit") || code.eq_ignore_ascii_case("exit") {
            return Ok(false);
        }

        println!("  {}Pairing...{}", color("yellow"), color("reset"));

        match try_pair(&config.server_url, &code, &config.data_dir).await {
            Ok((device_id, device_token, device_name)) => {
                *state.device_token.write().await = Some(device_token.clone());
                let token_path = format!("{}/device_token", config.data_dir);
                let _ = tokio::fs::write(&token_path, &device_token).await;
                return Ok(true);
            }
            Err(e) => {
                println!("  {}Failed: {}{}", color("red"), e, color("reset"));
                println!("  Try again or type {}quit{} to exit.", color("bold"), color("reset"));
                println!();
            }
        }
    }
}

fn print_banner(paired: bool) {
    println!();
    println!("  {}╔═══════════════════════════════════════════╗{}", color("cyan"), color("reset"));
    println!("  {}║       Aegis Cloud Agent v{:<16}║{}", color("cyan"), env!("CARGO_PKG_VERSION"), color("reset"));
    println!("  {}╚═══════════════════════════════════════════╝{}", color("cyan"), color("reset"));
    println!();
}

fn color(name: &str) -> &'static str {
    match name {
        "reset" => "\x1b[0m",
        "bold" => "\x1b[1m",
        "red" => "\x1b[31m",
        "green" => "\x1b[32m",
        "yellow" => "\x1b[33m",
        "cyan" => "\x1b[36m",
        _ => "",
    }
}

#[tokio::main]
async fn main() {
    // Initialize logging (only for service mode or behind-the-scenes)
    env_logger::Builder::from_env(
        env_logger::Env::default().default_filter_or("info")
    ).init();

    let config = AgentConfig::from_env();

    let run_as_service = std::env::var("AEGIS_SERVICE_MODE")
        .unwrap_or_default()
        .parse::<bool>()
        .unwrap_or(false);

    if run_as_service {
        match service::windows::run_as_service(config).await {
            Ok(()) => info!("Service exited normally"),
            Err(e) => error!("Service error: {}", e),
        }
    } else {
        match run_agent(config).await {
            Ok(()) => {}
            Err(e) => {
                println!("  \x1b[31mError: {}\x1b[0m", e);
            }
        }
    }
}
