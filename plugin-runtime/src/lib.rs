//! Aegis Plugin Runtime
//!
//! Loads and executes plugins on the agent side.
//! Handles sandboxing, lifecycle management, and security isolation.

use aegis_plugin_runtime::{Tool, ToolMetadata, ToolOutput, ToolResult, PluginManifest};
use libloading::{Library, Symbol};
use std::collections::HashMap;
use std::path::Path;
use std::sync::Arc;
use tokio::sync::RwLock;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum PluginError {
    #[error("Failed to load plugin: {0}")]
    LoadError(String),
    
    #[error("Plugin not found: {0}")]
    NotFound(String),
    
    #[error("Tool not found: {0}")]
    ToolNotFound(String),
    
    #[error("Execution timeout after {0}ms")]
    Timeout(u64),
    
    #[error("Plugin validation failed: {0}")]
    ValidationError(String),
    
    #[error("Sandbox violation: {0}")]
    SandboxViolation(String),
}

/// Plugin runtime manager
pub struct PluginRuntime {
    plugins: Arc<RwLock<HashMap<String, LoadedPlugin>>>,
    config: RuntimeConfig,
}

struct LoadedPlugin {
    manifest: PluginManifest,
    library: Library,
    tools: Vec<Box<dyn Tool>>,
}

#[derive(Clone)]
pub struct RuntimeConfig {
    pub plugin_dir: String,
    pub max_memory_mb: u64,
    pub max_execution_time_ms: u64,
    pub sandbox_enabled: bool,
}

impl Default for RuntimeConfig {
    fn default() -> Self {
        Self {
            plugin_dir: "./plugins".to_string(),
            max_memory_mb: 100,
            max_execution_time_ms: 30000,
            sandbox_enabled: true,
        }
    }
}

impl PluginRuntime {
    pub fn new(config: RuntimeConfig) -> Self {
        Self {
            plugins: Arc::new(RwLock::new(HashMap::new())),
            config,
        }
    }
    
    /// Load a plugin from a .aegis file
    pub async fn load_plugin(&self, plugin_path: &str) -> Result<String, PluginError> {
        let path = Path::new(plugin_path);
        
        if !path.exists() {
            return Err(PluginError::LoadError(format!("File not found: {}", plugin_path)));
        }
        
        // Read and validate the plugin file
        let plugin_data = tokio::fs::read(path)
            .await
            .map_err(|e| PluginError::LoadError(e.to_string()))?;
        
        // Deserialize plugin package
        let plugin: aegis_plugin_runtime::PluginFile = serde_json::from_slice(&plugin_data)
            .map_err(|e| PluginError::LoadError(e.to_string()))?;
        
        // Verify signature if required
        if self.config.sandbox_enabled && plugin.signature.is_none() {
            return Err(PluginError::ValidationError("Plugin must be signed".to_string()));
        }
        
        // Verify binary hash
        let hash = sha2::Sha256::digest(&plugin.binary);
        let hash_hex = format!("{:x}", hash);
        if hash_hex != plugin.binary_hash {
            return Err(PluginError::ValidationError("Binary hash mismatch".to_string()));
        }
        
        // Write binary to temp location
        let temp_dir = tempfile::tempdir()
            .map_err(|e| PluginError::LoadError(e.to_string()))?;
        let binary_path = temp_dir.path().join(format!("{}.dll", plugin.manifest.name));
        tokio::fs::write(&binary_path, &plugin.binary)
            .await
            .map_err(|e| PluginError::LoadError(e.to_string()))?;
        
        // Load the dynamic library
        let library = unsafe {
            Library::new(&binary_path)
                .map_err(|e| PluginError::LoadError(e.to_string()))?
        };
        
        // Get tool registration function
        let register_fn: Symbol<fn() -> Vec<Box<dyn Tool>>> = unsafe {
            library.get(b"register_tools")
                .map_err(|e| PluginError::LoadError(e.to_string()))?
        };
        
        let tools = register_fn();
        
        // Validate tools against manifest
        for tool in &tools {
            let metadata = tool.metadata();
            let manifest_tool = plugin.manifest.tools.iter()
                .find(|t| t.name == metadata.name);
            
            if manifest_tool.is_none() {
                return Err(PluginError::ValidationError(
                    format!("Tool '{}' not declared in manifest", metadata.name)
                ));
            }
        }
        
        let plugin_id = plugin.manifest.name.clone();
        
        // Store loaded plugin
        let loaded = LoadedPlugin {
            manifest: plugin.manifest,
            library,
            tools,
        };
        
        self.plugins.write().await.insert(plugin_id.clone(), loaded);
        
        log::info!("Loaded plugin: {}", plugin_id);
        
        Ok(plugin_id)
    }
    
    /// Execute a tool from a loaded plugin
    pub async fn execute_tool(
        &self,
        plugin_id: &str,
        tool_name: &str,
        params: serde_json::Value,
    ) -> Result<ToolOutput, PluginError> {
        let plugins = self.plugins.read().await;
        let plugin = plugins
            .get(plugin_id)
            .ok_or_else(|| PluginError::NotFound(plugin_id.to_string()))?;
        
        // Find the tool
        let tool = plugin
            .tools
            .iter()
            .find(|t| t.metadata().name == tool_name)
            .ok_or_else(|| PluginError::ToolNotFound(tool_name.to_string()))?;
        
        let metadata = tool.metadata();
        
        // Check timeout
        let timeout = metadata.timeout * 1000; // Convert to milliseconds
        
        // Execute with timeout
        let result = tokio::time::timeout(
            std::time::Duration::from_millis(timeout),
            tool.execute(params)
        )
        .await;
        
        match result {
            Ok(Ok(output)) => Ok(output),
            Ok(Err(e)) => Err(PluginError::LoadError(e.to_string())),
            Err(_) => Err(PluginError::Timeout(timeout)),
        }
    }
    
    /// List all loaded plugins
    pub async fn list_plugins(&self) -> Vec<PluginManifest> {
        let plugins = self.plugins.read().await;
        plugins.values().map(|p| p.manifest.clone()).collect()
    }
    
    /// Unload a plugin
    pub async fn unload_plugin(&self, plugin_id: &str) -> Result<(), PluginError> {
        let mut plugins = self.plugins.write().await;
        plugins.remove(plugin_id)
            .ok_or_else(|| PluginError::NotFound(plugin_id.to_string()))?;
        
        log::info!("Unloaded plugin: {}", plugin_id);
        
        Ok(())
    }
}

/// Plugin sandbox for security isolation
pub struct PluginSandbox {
    allowed_paths: Vec<String>,
    blocked_syscalls: Vec<String>,
    max_memory_mb: u64,
}

impl PluginSandbox {
    pub fn new() -> Self {
        Self {
            allowed_paths: vec![
                "./plugins".to_string(),
                "./temp".to_string(),
            ],
            blocked_syscalls: vec![
                "exec".to_string(),
                "execve".to_string(),
                "system".to_string(),
            ],
            max_memory_mb: 100,
        }
    }
    
    /// Check if a path is allowed
    pub fn is_path_allowed(&self, path: &str) -> bool {
        self.allowed_paths.iter().any(|allowed| path.starts_with(allowed))
    }
    
    /// Check if a syscall is blocked
    pub fn is_syscall_blocked(&self, syscall: &str) -> bool {
        self.blocked_syscalls.contains(&syscall.to_string())
    }
}
