//! Capability-based permission system for plugins
//! 
//! Plugins declare required capabilities in their manifest.
//! The runtime enforces these permissions before execution.
//! This creates a security boundary between plugins and the host system.

use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use thiserror::Error;

/// All available capabilities in the system
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum Capability {
    // Filesystem capabilities
    FilesystemRead,
    FilesystemWrite,
    FilesystemWriteTemp,
    FilesystemDelete,
    
    // Registry capabilities
    RegistryRead,
    RegistryWrite,
    RegistryDelete,
    
    // Process capabilities
    ProcessList,
    ProcessKill,
    ProcessStart,
    
    // Service capabilities
    ServiceList,
    ServiceStart,
    ServiceStop,
    ServiceRestart,
    
    // Network capabilities
    NetworkPing,
    NetworkHttp,
    NetworkTcp,
    NetworkDns,
    
    // System capabilities
    SystemInfo,
    SystemRestart,
    SystemShutdown,
    SystemSleep,
    
    // Security capabilities
    SecurityAudit,
    SecurityModify,
    
    // Execution capabilities
    CommandExecute,
    ScriptExecute,
    
    // Display capabilities
    DisplayMessage,
    DisplayNotification,
}

impl Capability {
    /// Get human-readable name
    pub fn display_name(&self) -> &'static str {
        match self {
            Capability::FilesystemRead => "Read Files",
            Capability::FilesystemWrite => "Write Files",
            Capability::FilesystemWriteTemp => "Write Temp Files",
            Capability::FilesystemDelete => "Delete Files",
            Capability::RegistryRead => "Read Registry",
            Capability::RegistryWrite => "Write Registry",
            Capability::RegistryDelete => "Delete Registry Keys",
            Capability::ProcessList => "List Processes",
            Capability::ProcessKill => "Kill Processes",
            Capability::ProcessStart => "Start Processes",
            Capability::ServiceList => "List Services",
            Capability::ServiceStart => "Start Services",
            Capability::ServiceStop => "Stop Services",
            Capability::ServiceRestart => "Restart Services",
            Capability::NetworkPing => "Ping Network",
            Capability::NetworkHttp => "Make HTTP Requests",
            Capability::NetworkTcp => "TCP Connections",
            Capability::NetworkDns => "DNS Queries",
            Capability::SystemInfo => "Read System Info",
            Capability::SystemRestart => "Restart System",
            Capability::SystemShutdown => "Shutdown System",
            Capability::SystemSleep => "Sleep/Hibernate",
            Capability::SecurityAudit => "Security Audit",
            Capability::SecurityModify => "Modify Security Settings",
            Capability::CommandExecute => "Execute Commands",
            Capability::ScriptExecute => "Execute Scripts",
            Capability::DisplayMessage => "Display Messages",
            Capability::DisplayNotification => "Show Notifications",
        }
    }
    
    /// Get risk level for this capability
    pub fn risk_level(&self) -> RiskLevel {
        match self {
            // Low risk - read-only operations
            Capability::FilesystemRead |
            Capability::FilesystemWriteTemp |
            Capability::RegistryRead |
            Capability::ProcessList |
            Capability::ServiceList |
            Capability::NetworkPing |
            Capability::NetworkDns |
            Capability::SystemInfo |
            Capability::SecurityAudit |
            Capability::DisplayMessage |
            Capability::DisplayNotification => RiskLevel::Low,
            
            // Medium risk - write operations
            Capability::FilesystemWrite |
            Capability::RegistryWrite |
            Capability::ProcessStart |
            Capability::ServiceStart |
            Capability::ServiceStop |
            Capability::ServiceRestart |
            Capability::NetworkHttp |
            Capability::NetworkTcp |
            Capability::ScriptExecute => RiskLevel::Medium,
            
            // High risk - destructive operations
            Capability::FilesystemDelete |
            Capability::RegistryDelete |
            Capability::ProcessKill |
            Capability::CommandExecute |
            Capability::SecurityModify => RiskLevel::High,
            
            // Critical risk - system-level operations
            Capability::SystemRestart |
            Capability::SystemShutdown |
            Capability::SystemSleep => RiskLevel::Critical,
        }
    }
    
    /// Get description for permission prompt
    pub fn description(&self) -> &'static str {
        match self {
            Capability::FilesystemRead => "Read files from the filesystem",
            Capability::FilesystemWrite => "Write files to the filesystem",
            Capability::FilesystemWriteTemp => "Write files to temporary directories",
            Capability::FilesystemDelete => "Delete files from the filesystem",
            Capability::RegistryRead => "Read Windows Registry keys",
            Capability::RegistryWrite => "Write Windows Registry keys",
            Capability::RegistryDelete => "Delete Windows Registry keys",
            Capability::ProcessList => "View running processes",
            Capability::ProcessKill => "Terminate running processes",
            Capability::ProcessStart => "Start new processes",
            Capability::ServiceList => "View Windows services",
            Capability::ServiceStart => "Start Windows services",
            Capability::ServiceStop => "Stop Windows services",
            Capability::ServiceRestart => "Restart Windows services",
            Capability::NetworkPing => "Ping network hosts",
            Capability::NetworkHttp => "Make HTTP/HTTPS requests",
            Capability::NetworkTcp => "Open TCP connections",
            Capability::NetworkDns => "Perform DNS lookups",
            Capability::SystemInfo => "Access system information",
            Capability::SystemRestart => "Restart the computer",
            Capability::SystemShutdown => "Shutdown the computer",
            Capability::SystemSleep => "Put the computer to sleep",
            Capability::SecurityAudit => "Audit security settings",
            Capability::SecurityModify => "Modify security settings",
            Capability::CommandExecute => "Execute system commands",
            Capability::ScriptExecute => "Execute scripts",
            Capability::DisplayMessage => "Display messages to user",
            Capability::DisplayNotification => "Show desktop notifications",
        }
    }
}

/// Risk level for capabilities
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum RiskLevel {
    Low,
    Medium,
    High,
    Critical,
}

/// Capability declaration in plugin manifest
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CapabilityManifest {
    /// Required capabilities
    pub required: HashSet<Capability>,
    
    /// Optional capabilities (user can deny)
    pub optional: HashSet<Capability>,
    
    /// Denied capabilities (plugin won't work without these)
    pub denied: HashSet<Capability>,
}

impl CapabilityManifest {
    /// Create new capability manifest
    pub fn new() -> Self {
        Self {
            required: HashSet::new(),
            optional: HashSet::new(),
            denied: HashSet::new(),
        }
    }
    
    /// Add required capability
    pub fn require(&mut self, capability: Capability) -> &mut Self {
        self.required.insert(capability);
        self
    }
    
    /// Add optional capability
    pub fn optional(&mut self, capability: Capability) -> &mut Self {
        self.optional.insert(capability);
        self
    }
    
    /// Add denied capability
    pub fn deny(&mut self, capability: Capability) -> &mut Self {
        self.denied.insert(capability);
        self
    }
    
    /// Get highest risk level
    pub fn highest_risk(&self) -> RiskLevel {
        self.required
            .iter()
            .chain(self.optional.iter())
            .map(|c| c.risk_level())
            .max()
            .unwrap_or(RiskLevel::Low)
    }
    
    /// Check if manifest is valid (no conflicts)
    pub fn is_valid(&self) -> bool {
        // Can't require and deny the same capability
        !self.required.intersection(&self.denied).next().is_some()
    }
}

impl Default for CapabilityManifest {
    fn default() -> Self {
        Self::new()
    }
}

/// Capability check result
#[derive(Debug, Clone)]
pub struct CapabilityCheck {
    pub granted: HashSet<Capability>,
    pub denied: HashSet<Capability>,
    pub requires_approval: HashSet<Capability>,
}

/// Capability enforcement context
#[derive(Clone)]
pub struct CapabilityContext {
    /// Granted capabilities for current execution
    granted: HashSet<Capability>,
    
    /// Audit log
    audit_log: Vec<CapabilityAuditEntry>,
    
    /// Plugin ID for audit logging
    plugin_id: String,
    
    /// Tool name for audit logging
    tool_name: String,
}

/// Audit log entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CapabilityAuditEntry {
    pub capability: Capability,
    pub action: CapabilityAction,
    pub result: CapabilityResult,
    pub timestamp: chrono::DateTime<chrono::Utc>,
    pub plugin_id: String,
    pub tool_name: String,
}

/// Capability action
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum CapabilityAction {
    Check,
    Use,
    Deny,
}

/// Capability check result
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum CapabilityResult {
    Granted,
    Denied,
    RequiresApproval,
}

impl CapabilityContext {
    /// Create new capability context
    pub fn new(granted: HashSet<Capability>, plugin_id: String, tool_name: String) -> Self {
        Self {
            granted,
            audit_log: Vec::new(),
            plugin_id,
            tool_name,
        }
    }
    
    /// Check if capability is granted
    pub fn has(&self, capability: Capability) -> bool {
        self.granted.contains(&capability)
    }
    
    /// Get all granted capabilities
    pub fn granted(&self) -> &HashSet<Capability> {
        &self.granted
    }
    
    /// Get plugin ID
    pub fn plugin_id(&self) -> &str {
        &self.plugin_id
    }
    
    /// Get tool name
    pub fn tool_name(&self) -> &str {
        &self.tool_name
    }
    
    /// Check if capability is granted
    pub fn check(&mut self, capability: Capability) -> CapabilityResult {
        let result = if self.granted.contains(&capability) {
            CapabilityResult::Granted
        } else if capability.risk_level() >= RiskLevel::High {
            CapabilityResult::RequiresApproval
        } else {
            CapabilityResult::Denied
        };
        
        // Log audit entry
        self.audit_log.push(CapabilityAuditEntry {
            capability,
            action: CapabilityAction::Check,
            result,
            timestamp: chrono::Utc::now(),
            plugin_id: self.plugin_id.clone(),
            tool_name: self.tool_name.clone(),
        });
        
        result
    }
    
    /// Check if capability is available (throws error if not)
    pub fn require(&mut self, capability: Capability) -> Result<(), CapabilityError> {
        match self.check(capability) {
            CapabilityResult::Granted => Ok(()),
            CapabilityResult::Denied => Err(CapabilityError::Denied(capability)),
            CapabilityResult::RequiresApproval => Err(CapabilityError::RequiresApproval(capability)),
        }
    }
    
    /// Get audit log
    pub fn audit_log(&self) -> &[CapabilityAuditEntry] {
        &self.audit_log
    }
}

/// Capability errors
#[derive(Error, Debug)]
pub enum CapabilityError {
    #[error("Capability '{0}' is not granted")]
    Denied(Capability),
    
    #[error("Capability '{0}' requires admin approval")]
    RequiresApproval(Capability),
    
    #[error("Invalid capability manifest: {0}")]
    InvalidManifest(String),
}

/// Capability checker (validates manifest against policy)
pub struct CapabilityChecker {
    /// Allowed capabilities for this policy
    allowed: HashSet<Capability>,
    
    /// Requires approval for these capabilities
    requires_approval: HashSet<Capability>,
}

impl CapabilityChecker {
    /// Create new capability checker with default policy
    pub fn new() -> Self {
        let mut allowed = HashSet::new();
        let mut requires_approval = HashSet::new();
        
        // Allow low-risk capabilities
        allowed.insert(Capability::FilesystemRead);
        allowed.insert(Capability::FilesystemWriteTemp);
        allowed.insert(Capability::RegistryRead);
        allowed.insert(Capability::ProcessList);
        allowed.insert(Capability::ServiceList);
        allowed.insert(Capability::NetworkPing);
        allowed.insert(Capability::NetworkDns);
        allowed.insert(Capability::SystemInfo);
        allowed.insert(Capability::SecurityAudit);
        allowed.insert(Capability::DisplayMessage);
        allowed.insert(Capability::DisplayNotification);
        
        // Require approval for medium-risk
        requires_approval.insert(Capability::FilesystemWrite);
        requires_approval.insert(Capability::RegistryWrite);
        requires_approval.insert(Capability::ProcessStart);
        requires_approval.insert(Capability::ServiceStart);
        requires_approval.insert(Capability::ServiceStop);
        requires_approval.insert(Capability::ServiceRestart);
        requires_approval.insert(Capability::NetworkHttp);
        requires_approval.insert(Capability::NetworkTcp);
        requires_approval.insert(Capability::ScriptExecute);
        
        // Require approval for high-risk
        requires_approval.insert(Capability::FilesystemDelete);
        requires_approval.insert(Capability::RegistryDelete);
        requires_approval.insert(Capability::ProcessKill);
        requires_approval.insert(Capability::CommandExecute);
        requires_approval.insert(Capability::SecurityModify);
        
        // Require approval for critical
        requires_approval.insert(Capability::SystemRestart);
        requires_approval.insert(Capability::SystemShutdown);
        requires_approval.insert(Capability::SystemSleep);
        
        Self {
            allowed,
            requires_approval,
        }
    }
    
    /// Check capability manifest against policy
    pub fn check(&self, manifest: &CapabilityManifest) -> CapabilityCheck {
        let mut granted = HashSet::new();
        let mut denied = HashSet::new();
        let mut requires_approval = HashSet::new();
        
        for capability in &manifest.required {
            if self.requires_approval.contains(capability) {
                requires_approval.insert(*capability);
            } else if self.allowed.contains(capability) {
                granted.insert(*capability);
            } else {
                denied.insert(*capability);
            }
        }
        
        CapabilityCheck {
            granted,
            denied,
            requires_approval,
        }
    }
}

impl Default for CapabilityChecker {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_capability_manifest() {
        let mut manifest = CapabilityManifest::new();
        manifest.require(Capability::FilesystemRead);
        manifest.require(Capability::RegistryRead);
        manifest.optional(Capability::NetworkPing);
        
        assert!(manifest.is_valid());
        assert_eq!(manifest.highest_risk(), RiskLevel::Low);
    }
    
    #[test]
    fn test_capability_checker() {
        let checker = CapabilityChecker::new();
        
        let mut manifest = CapabilityManifest::new();
        manifest.require(Capability::FilesystemRead);
        manifest.require(Capability::ServiceRestart);
        
        let check = checker.check(&manifest);
        
        assert!(check.granted.contains(&Capability::FilesystemRead));
        assert!(check.requires_approval.contains(&Capability::ServiceRestart));
    }
    
    #[test]
    fn test_capability_context() {
        let mut granted = HashSet::new();
        granted.insert(Capability::FilesystemRead);
        
        let mut context = CapabilityContext::new(granted);
        
        assert_eq!(
            context.check(Capability::FilesystemRead, "test-plugin", "test-tool"),
            CapabilityResult::Granted
        );
        
        assert_eq!(
            context.check(Capability::ProcessKill, "test-plugin", "test-tool"),
            CapabilityResult::RequiresApproval
        );
    }
}
