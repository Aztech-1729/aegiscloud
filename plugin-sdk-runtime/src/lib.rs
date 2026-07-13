//! Aegis Plugin Runtime Types
//!
//! Core types used by the plugin SDK and agent runtime.

use serde::{Deserialize, Serialize};
use thiserror::Error;
use crate::capabilities::{CapabilityManifest, CapabilityContext};
use crate::capability_layer::CapabilityLayer;

/// Tool metadata describing a plugin tool
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolMetadata {
    /// Unique tool name (snake_case)
    pub name: String,
    /// Human-readable description
    pub description: String,
    /// Category: system, process, file, network, security, maintenance
    pub category: String,
    /// Risk level: low, medium, high, critical
    pub risk_level: String,
    /// Required capabilities
    pub capabilities: CapabilityManifest,
    /// Whether admin approval is required
    pub requires_approval: bool,
    /// Execution timeout in seconds
    pub timeout: u64,
}

/// Trait that all plugin tools must implement
#[async_trait::async_trait]
pub trait Tool: Send + Sync {
    /// Get tool metadata
    fn metadata(&self) -> ToolMetadata;
    
    /// Execute the tool with given parameters
    async fn execute(&self, params: serde_json::Value) -> ToolResult;
}

/// Tool execution context with capability layer
pub struct ToolContext {
    capability_context: CapabilityContext,
}

impl ToolContext {
    /// Create new tool context
    pub fn new(capability_context: CapabilityContext) -> Self {
        Self { capability_context }
    }
    
    /// Get capability layer for accessing OS capabilities
    pub fn capabilities(&mut self) -> CapabilityLayer {
        CapabilityLayer::new(self.capability_context.clone())
    }
    
    /// Check if a capability is granted
    pub fn has_capability(&self, capability: crate::capabilities::Capability) -> bool {
        self.capability_context.has(capability)
    }
}

/// Result of tool execution
pub type ToolResult = Result<ToolOutput, ToolError>;

/// Successful tool output
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolOutput {
    /// Whether execution succeeded
    pub success: bool,
    /// Human-readable message
    pub message: String,
    /// Structured output data
    pub data: serde_json::Value,
    /// Execution duration in milliseconds
    #[serde(skip_serializing_if = "Option::is_none")]
    pub duration_ms: Option<u64>,
}

impl ToolOutput {
    /// Create a successful output
    pub fn success<T: Serialize>(data: T) -> Self {
        Self {
            success: true,
            message: "Success".to_string(),
            data: serde_json::to_value(data).unwrap_or(serde_json::Value::Null),
            duration_ms: None,
        }
    }
    
    /// Create a successful output with a message
    pub fn success_with_message<T: Serialize>(message: &str, data: T) -> Self {
        Self {
            success: true,
            message: message.to_string(),
            data: serde_json::to_value(data).unwrap_or(serde_json::Value::Null),
            duration_ms: None,
        }
    }
}

/// Tool execution errors
#[derive(Debug, Error, Serialize, Deserialize)]
pub enum ToolError {
    #[error("Invalid parameters: {0}")]
    InvalidParameters(String),
    
    #[error("Execution failed: {0}")]
    ExecutionFailed(String),
    
    #[error("Permission denied: {0}")]
    PermissionDenied(String),
    
    #[error("Resource not found: {0}")]
    NotFound(String),
    
    #[error("Timeout after {0} seconds")]
    Timeout(u64),
    
    #[error("Capability denied: {0}")]
    CapabilityDenied(String),
    
    #[error("Internal error: {0}")]
    Internal(String),
}

/// Plugin manifest
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginManifest {
    /// Plugin name
    pub name: String,
    /// Plugin version (semver)
    pub version: String,
    /// Author name/email
    pub author: String,
    /// Plugin description
    pub description: String,
    /// Plugin homepage URL
    #[serde(skip_serializing_if = "Option::is_none")]
    pub homepage: Option<String>,
    /// License identifier
    pub license: String,
    /// List of tools provided
    pub tools: Vec<ToolMetadata>,
    /// Minimum agent version required
    #[serde(skip_serializing_if = "Option::is_none")]
    pub min_agent_version: Option<String>,
    /// Maximum agent version supported
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_agent_version: Option<String>,
    /// Required permissions
    pub permissions: Vec<String>,
    /// Target platform
    pub platform: String,
    /// SDK version used to build this plugin
    pub sdk_version: String,
}

/// Plugin file format
#[derive(Debug, Serialize, Deserialize)]
pub struct PluginFile {
    /// Plugin manifest
    pub manifest: PluginManifest,
    /// Compiled plugin binary (WASM or native)
    #[serde(with = "base64_serde")]
    pub binary: Vec<u8>,
    /// SHA-256 hash of binary
    pub binary_hash: String,
    /// Digital signature (developer signature)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub developer_signature: Option<String>,
    /// Marketplace signature (added during publish)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub marketplace_signature: Option<String>,
    /// Integrity hash (hash of manifest + binary)
    pub integrity_hash: String,
}

mod base64_serde {
    use serde::{Deserialize, Deserializer, Serializer};
    use base64::{Engine as _, engine::general_purpose::STANDARD};
    
    pub fn serialize<S>(bytes: &Vec<u8>, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_str(&STANDARD.encode(bytes))
    }
    
    pub fn deserialize<'de, D>(deserializer: D) -> Result<Vec<u8>, D::Error>
    where
        D: Deserializer<'de>,
    {
        let s = String::deserialize(deserializer)?;
        STANDARD.decode(s).map_err(serde::de::Error::custom)
    }
}

/// Plugin validation result
#[derive(Debug, Serialize, Deserialize)]
pub struct ValidationResult {
    pub valid: bool,
    pub errors: Vec<String>,
    pub warnings: Vec<String>,
}

/// Marketplace listing
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginListing {
    pub id: String,
    pub name: String,
    pub version: String,
    pub author: String,
    pub description: String,
    pub category: String,
    pub download_count: u64,
    pub rating: f32,
    pub rating_count: u32,
    pub size_bytes: u64,
    pub published_at: String,
    pub updated_at: String,
    pub tools: Vec<String>,
    pub tags: Vec<String>,
    /// Screenshots (URLs)
    pub screenshots: Vec<String>,
    /// Supported capabilities
    pub capabilities: Vec<String>,
    /// Security review status
    pub security_review: String,
    /// Source code availability
    pub source_available: bool,
    /// Changelog
    pub changelog: Vec<String>,
    /// Release notes
    pub release_notes: String,
}

/// Inventory registration for tools (auto-discovery)
pub mod inventory {
    pub use ::inventory::*;
}

pub mod capabilities;
pub mod capability_layer;

/// Prelude for convenient imports
pub mod prelude {
    pub use crate::{Tool, ToolMetadata, ToolOutput, ToolResult, ToolContext, ToolError};
    pub use crate::capabilities::{
        Capability, CapabilityManifest, CapabilityContext,
        CapabilityError, RiskLevel,
    };
    pub use crate::capability_layer::*;
    pub use async_trait::async_trait;
    pub use serde_json;
}

// Re-export base64 for manifest serialization
use base64;
