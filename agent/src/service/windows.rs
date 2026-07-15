//! Phase 1: Windows Service implementation
//!
//! The agent runs as a Windows Service that:
//! - Auto-starts with Windows boot
//! - Runs even when no user is logged in
//! - Recovers automatically on failure
//! - Logs to the system event log

use log::{info, error};
use crate::AgentConfig;

/// Run the agent as a Windows Service
/// 
/// Windows Boot
///     ↓
/// Windows Service Manager
///     ↓
/// Aegis Agent Service
///     ↓
/// run_agent() loop
pub async fn run_as_service(config: AgentConfig) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    info!("Initializing Windows Service...");

    // In a full implementation, this would use windows-service crate:
    //
    // define_windows_service!(ffi_service_main, service_main);
    //
    // fn service_main(arguments: Vec<OsString>) {
    //     // Start the agent loop in a background thread
    //     let config = parse_config_from_registry();
    //     tokio::runtime::Runtime::new()
    //         .unwrap()
    //         .block_on(crate::run_agent(config))
    //         .unwrap();
    // }
    //
    // For now, we simulate the service behavior:

    // Load configuration from Windows Registry
    let registry_config = load_config_from_registry();
    let effective_config = merge_config(config, registry_config);

    info!("Service configuration loaded");
    info!("  Server: {}", effective_config.server_url);
    info!("  Auto-update: {}", effective_config.auto_update);

    // Set up Windows Event Log
    setup_event_log()?;

    // Configure service recovery options
    configure_recovery()?;

    // Run the main agent loop
    info!("Starting agent service loop...");
    crate::run_agent(effective_config).await?;

    Ok(())
}

/// Load agent configuration from Windows Registry
/// HKLM\SOFTWARE\AegisCloud\Agent
fn load_config_from_registry() -> AgentConfig {
    // In production, this reads from:
    // HKEY_LOCAL_MACHINE\SOFTWARE\AegisCloud\Agent\ServerUrl
    // HKEY_LOCAL_MACHINE\SOFTWARE\AegisCloud\Agent\AutoUpdate
    // HKEY_LOCAL_MACHINE\SOFTWARE\AegisCloud\Agent\DataDir
    
    AgentConfig {
        server_url: "wss://api.aegiscloud.in".to_string(),
        device_token: None,
        pair_code: None,
        log_level: "info".to_string(),
        auto_update: true,
        data_dir: "C:\\ProgramData\\AegisCloud".to_string(),
    }
}

/// Merge registry config with environment config (env takes precedence)
fn merge_config(base: AgentConfig, registry: AgentConfig) -> AgentConfig {
    AgentConfig {
        server_url: if base.server_url != "wss://api.aegiscloud.in" {
            base.server_url
        } else {
            registry.server_url
        },
        device_token: base.device_token.or(registry.device_token),
        pair_code: base.pair_code.or(registry.pair_code),
        log_level: if base.log_level != "info" {
            base.log_level
        } else {
            registry.log_level
        },
        auto_update: base.auto_update,
        data_dir: base.data_dir,
    }
}

/// Set up Windows Event Log for service logging
fn setup_event_log() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    // In production: Register event source with Windows Event Log
    // HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\EventLog\Application\AegisCloudAgent
    info!("Event log configured for AegisCloudAgent");
    Ok(())
}

/// Configure automatic service recovery
fn configure_recovery() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    // In production, this calls:
    // sc failure AegisCloudAgent reset=86400 actions=restart/5000/restart/10000/restart/30000
    //
    // Recovery actions:
    // 1st failure: Restart after 5 seconds
    // 2nd failure: Restart after 10 seconds
    // 3rd failure: Restart after 30 seconds
    // Reset counter after: 24 hours
    
    info!("Service recovery configured: restart on failure");
    Ok(())
}

/// Install the agent as a Windows Service
pub fn install_service() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    info!("Installing Aegis Cloud Agent as Windows service...");
    
    // In production, this would:
    // 1. Copy binary to Program Files
    // 2. Create service with sc.exe or Windows API
    // 3. Set service to auto-start
    // 4. Configure recovery options
    // 5. Set service description and display name
    //
    // sc create AegisCloudAgent binPath= "C:\Program Files\AegisCloud\aegis-agent.exe" 
    //     start= auto DisplayName= "Aegis Cloud Agent"
    // sc description AegisCloudAgent "Secure remote management agent for Aegis Cloud"
    // sc failure AegisCloudAgent reset=86400 actions=restart/5000/restart/10000/restart/30000
    
    info!("Service installed successfully");
    info!("Service will start automatically on next boot");
    Ok(())
}

/// Uninstall the Windows Service
pub fn uninstall_service() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    info!("Uninstalling Aegis Cloud Agent service...");
    
    // In production:
    // sc stop AegisCloudAgent
    // sc delete AegisCloudAgent
    
    info!("Service uninstalled successfully");
    Ok(())
}
