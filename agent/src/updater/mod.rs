//! Phase 6: Auto-Update System
//!
//! Flow:
//!   Server → Agent checks for update
//!     ↓
//!   Download new binary
//!     ↓
//!   Verify SHA256 hash
//!     ↓
//!   Verify Ed25519 signature
//!     ↓
//!   Replace current binary
//!     ↓
//!   Restart service

use log::{info, error, warn};
use serde::{Deserialize, Serialize};
use crate::AgentState;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct UpdateInfo {
    pub version: String,
    pub download_url: String,
    pub sha256: String,
    pub signature: String,
    pub release_notes: Option<String>,
    pub is_mandatory: bool,
}

#[derive(Debug, Serialize, Deserialize)]
struct UpdateCheckResponse {
    pub update_available: bool,
    #[serde(default)]
    pub latest_version: Option<String>,
    #[serde(default)]
    pub download_url: Option<String>,
    #[serde(default)]
    pub sha256: Option<String>,
    #[serde(default)]
    pub signature: Option<String>,
    #[serde(default)]
    pub release_notes: Option<String>,
    #[serde(default)]
    pub is_mandatory: bool,
}

/// Run the update check loop in the background
pub async fn run_update_loop(state: AgentState) {
    let check_interval = tokio::time::Duration::from_secs(3600); // Check every hour
    
    loop {
        tokio::time::sleep(check_interval).await;
        
        if *state.shutdown.read().await {
            break;
        }

        info!("Checking for updates...");
        
        match check_for_update(&state).await {
            Ok(Some(update_info)) => {
                info!("Update available: v{}", update_info.version);
                
                if update_info.is_mandatory {
                    info!("Mandatory update — applying immediately");
                }

                match apply_update(&state, &update_info).await {
                    Ok(()) => {
                        info!("Update to v{} applied successfully", update_info.version);
                        // The service will restart and the new binary will take over
                    }
                    Err(e) => {
                        error!("Failed to apply update: {}", e);
                    }
                }
            }
            Ok(None) => {
                info!("Agent is up to date (v{})", env!("CARGO_PKG_VERSION"));
            }
            Err(e) => {
                warn!("Update check failed: {}", e);
            }
        }
    }
}

/// Check the server for available updates
async fn check_for_update(state: &AgentState) -> Result<Option<UpdateInfo>, Box<dyn std::error::Error + Send + Sync>> {
    let token = state.device_token.read().await.clone()
        .ok_or("No device token available")?;

    let client = reqwest::Client::new();
    let url = format!("{}/api/v1/updates/check", state.config.server_url.replace("ws://", "http://").replace("wss://", "https://"));

    let response = client
        .get(&url)
        .header("Authorization", format!("Bearer {}", token))
        .header("X-Agent-Version", env!("CARGO_PKG_VERSION"))
        .send()
        .await?;

    if !response.status().is_success() {
        return Err(format!("Server returned status {}", response.status()).into());
    }

    let check: UpdateCheckResponse = response.json().await?;

    if !check.update_available {
        return Ok(None);
    }

    Ok(Some(UpdateInfo {
        version: check.latest_version.unwrap_or_default(),
        download_url: check.download_url.unwrap_or_default(),
        sha256: check.sha256.unwrap_or_default(),
        signature: check.signature.unwrap_or_default(),
        release_notes: check.release_notes,
        is_mandatory: check.is_mandatory,
    }))
}

/// Download, verify, and apply an update
async fn apply_update(state: &AgentState, update: &UpdateInfo) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let update_dir = format!("{}/updates", state.config.data_dir);
    let download_path = format!("{}/aegis-agent-{}.exe", update_dir, update.version);
    let current_exe = std::env::current_exe()?;
    let backup_path = format!("{}.backup", current_exe.to_string_lossy());

    // Step 1: Download new binary
    info!("Downloading update v{}...", update.version);
    let client = reqwest::Client::new();
    let response = client.get(&update.download_url).send().await?;
    
    if !response.status().is_success() {
        return Err("Failed to download update".into());
    }

    let bytes = response.bytes().await?;
    tokio::fs::write(&download_path, &bytes).await?;
    info!("Downloaded {} bytes", bytes.len());

    // Step 2: Verify SHA256 hash
    info!("Verifying SHA256 hash...");
    let hash = crate::security::crypto::sha256_file(&download_path).await?;
    if hash != update.sha256 {
        tokio::fs::remove_file(&download_path).await?;
        return Err(format!(
            "SHA256 mismatch! Expected: {}, Got: {}",
            update.sha256, hash
        ).into());
    }
    info!("SHA256 verified ✓");

    // Step 3: Verify Ed25519 signature
    info!("Verifying signature...");
    let valid = crate::security::crypto::verify_signature(
        &hash,
        &update.signature,
    )?;
    if !valid {
        tokio::fs::remove_file(&download_path).await?;
        return Err("Signature verification failed!".into());
    }
    info!("Signature verified ✓");

    // Step 4: Backup current binary
    info!("Creating backup of current binary...");
    tokio::fs::copy(&current_exe, &backup_path).await?;

    // Step 5: Replace binary
    // On Windows, we can't replace a running binary directly.
    // Instead, we rename current → .old, move new → current, then restart.
    info!("Replacing binary...");
    let old_path = format!("{}.old", current_exe.to_string_lossy());
    
    // Rename current to .old
    tokio::fs::rename(&current_exe, &old_path).await?;
    
    // Move new to current location
    tokio::fs::rename(&download_path, &current_exe).await?;

    // Step 6: Clean up old backup
    let _ = tokio::fs::remove_file(&backup_path).await;

    info!("Update applied. Service will restart...");
    
    // Step 7: Signal shutdown — the service manager will restart us
    *state.shutdown.write().await = true;

    Ok(())
}
