//! Network Monitor — Detect and adapt to network changes
//!
//! The agent must handle:
//! - WiFi → Ethernet transitions
//! - VPN connect/disconnect
//! - Network interface changes
//! - IP address changes
//! - DNS changes
//! - Temporary outages
//! - System sleep/wake events

use std::sync::Arc;
use tokio::sync::RwLock;
use log::{info, warn, error};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

/// Network state snapshot
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkState {
    pub is_online: bool,
    pub interface_type: Option<String>,  // "wifi", "ethernet", "vpn"
    pub ip_address: Option<String>,
    pub gateway: Option<String>,
    pub dns_servers: Vec<String>,
    pub last_check: DateTime<Utc>,
    pub latency_ms: Option<u64>,
}

/// Network change event
#[derive(Debug, Clone)]
pub enum NetworkEvent {
    Online { interface: String },
    Offline,
    InterfaceChanged { from: String, to: String },
    IpChanged { old: String, new: String },
    LatencySpike { ms: u64 },
}

/// Network monitor — tracks network state and detects changes
pub struct NetworkMonitor {
    state: Arc<RwLock<NetworkState>>,
    change_listeners: Arc<RwLock<Vec<tokio::sync::mpsc::UnboundedSender<NetworkEvent>>>>,
    history: Arc<RwLock<Vec<(DateTime<Utc>, NetworkEvent)>>>,
}

impl NetworkMonitor {
    pub fn new() -> Self {
        Self {
            state: Arc::new(RwLock::new(NetworkState {
                is_online: false,
                interface_type: None,
                ip_address: None,
                gateway: None,
                dns_servers: Vec::new(),
                last_check: Utc::now(),
                latency_ms: None,
            })),
            change_listeners: Arc::new(RwLock::new(Vec::new())),
            history: Arc::new(RwLock::new(Vec::new())),
        }
    }

    /// Check current network status
    pub async fn check_network(&self) -> NetworkState {
        let new_state = self.gather_network_info().await;
        let old_state = self.state.read().await.clone();
        
        // Detect changes
        self.detect_changes(&old_state, &new_state).await;
        
        // Update state
        *self.state.write().await = new_state.clone();
        
        new_state
    }

    /// Gather actual network information
    async fn gather_network_info(&self) -> NetworkState {
        let mut state = NetworkState {
            is_online: false,
            interface_type: None,
            ip_address: None,
            gateway: None,
            dns_servers: Vec::new(),
            last_check: Utc::now(),
            latency_ms: None,
        };

        // Check connectivity by trying to resolve DNS
        let is_online = tokio::net::TcpStream::connect("1.1.1.1:53")
            .await
            .is_ok();

        state.is_online = is_online;

        if is_online {
            // Get IP address
            if let Ok(output) = tokio::process::Command::new("ipconfig")
                .output()
                .await
            {
                let output_str = String::from_utf8_lossy(&output.stdout);
                
                // Parse IPv4 address
                for line in output_str.lines() {
                    if line.contains("IPv4 Address") || line.contains("IPv4") {
                        if let Some(ip) = line.split(':').nth(1) {
                            let ip = ip.trim().to_string();
                            if !ip.is_empty() {
                                state.ip_address = Some(ip);
                            }
                        }
                    }
                }

                // Detect interface type
                if output_str.contains("Wireless") || output_str.contains("Wi-Fi") {
                    state.interface_type = Some("wifi".to_string());
                } else if output_str.contains("Ethernet") {
                    state.interface_type = Some("ethernet".to_string());
                }

                // Check for VPN
                if output_str.contains("VPN") || output_str.contains("TAP") || output_str.contains("Tunnel") {
                    state.interface_type = Some("vpn".to_string());
                }
            }

            // Measure latency
            let start = std::time::Instant::now();
            if tokio::net::TcpStream::connect("8.8.8.8:443").await.is_ok() {
                state.latency_ms = Some(start.elapsed().as_millis() as u64);
            }
        }

        state
    }

    /// Detect network changes and emit events
    async fn detect_changes(&self, old: &NetworkState, new: &NetworkState) {
        // Online/Offline transition
        if !old.is_online && new.is_online {
            let event = NetworkEvent::Online {
                interface: new.interface_type.clone().unwrap_or_default(),
            };
            self.emit_event(event).await;
        } else if old.is_online && !new.is_online {
            self.emit_event(NetworkEvent::Offline).await;
        }

        // Interface changed
        if old.interface_type != new.interface_type {
            if let (Some(old_type), Some(new_type)) = (&old.interface_type, &new.interface_type) {
                let event = NetworkEvent::InterfaceChanged {
                    from: old_type.clone(),
                    to: new_type.clone(),
                };
                self.emit_event(event).await;
            }
        }

        // IP changed
        if old.ip_address != new.ip_address {
            if let (Some(old_ip), Some(new_ip)) = (&old.ip_address, &new.ip_address) {
                let event = NetworkEvent::IpChanged {
                    old: old_ip.clone(),
                    new: new_ip.clone(),
                };
                self.emit_event(event).await;
            }
        }

        // Latency spike
        if let Some(latency) = new.latency_ms {
            if latency > 500 {
                let event = NetworkEvent::LatencySpike { ms: latency };
                self.emit_event(event).await;
            }
        }
    }

    /// Emit a network event to all listeners
    async fn emit_event(&self, event: NetworkEvent) {
        info!("Network event: {:?}", event);
        
        // Record in history
        {
            let mut history = self.history.write().await;
            history.push((Utc::now(), event.clone()));
            // Keep last 100 events
            if history.len() > 100 {
                history.drain(..history.len() - 100);
            }
        }

        // Notify listeners
        let listeners = self.change_listeners.read().await;
        for listener in listeners.iter() {
            let _ = listener.send(event.clone());
        }
    }

    /// Subscribe to network change events
    pub async fn subscribe(&self) -> tokio::sync::mpsc::UnboundedReceiver<NetworkEvent> {
        let (tx, rx) = tokio::sync::mpsc::unbounded_channel();
        self.change_listeners.write().await.push(tx);
        rx
    }

    /// Check if network is online
    pub async fn is_online(&self) -> bool {
        self.state.read().await.is_online
    }

    /// Get current network state
    pub async fn get_state(&self) -> NetworkState {
        self.state.read().await.clone()
    }

    /// Get network history
    pub async fn get_history(&self) -> Vec<(DateTime<Utc>, NetworkEvent)> {
        self.history.read().await.clone()
    }

    /// Start periodic network monitoring
    pub async fn start_monitoring(self: &Arc<Self>) {
        let monitor = self.clone();
        tokio::spawn(async move {
            let check_interval = tokio::time::Duration::from_secs(30);
            
            loop {
                monitor.check_network().await;
                tokio::time::sleep(check_interval).await;
            }
        });
    }
}

/// Detect Windows sleep/wake events
pub async fn detect_power_events() -> tokio::sync::mpsc::UnboundedReceiver<PowerEvent> {
    let (tx, rx) = tokio::sync::mpsc::unbounded_channel();
    
    // Monitor system power state changes
    // On Windows, this would use SetThreadExecutionState and power event notifications
    // For now, we detect wake by checking time gaps
    tokio::spawn(async move {
        let mut last_check = Utc::now();
        let check_interval = tokio::time::Duration::from_secs(10);
        
        loop {
            tokio::time::sleep(check_interval).await;
            let now = Utc::now();
            let elapsed = now.signed_duration_since(last_check);
            
            // If more than 20 seconds passed but we only waited 10, we likely slept
            if elapsed.num_seconds() > 20 {
                info!("System wake detected ({}s gap)", elapsed.num_seconds());
                let _ = tx.send(PowerEvent::Wake {
                    sleep_duration_secs: elapsed.num_seconds() as u64,
                });
            }
            
            last_check = now;
        }
    });
    
    rx
}

#[derive(Debug, Clone)]
pub enum PowerEvent {
    Sleep,
    Wake { sleep_duration_secs: u64 },
    BatteryLow,
    PowerConnected,
}
