# Aegis Cloud Capability Architecture

## Overview

Aegis Cloud uses a **capability-based security model** that sits between plugins and the Windows API. Plugins never call operating system functions directly. Instead, they use capability methods that enforce permissions, provide audit logging, and maintain sandboxing.

```
Plugin Tool
    ↓
Aegis SDK (#[tool] macro)
    ↓
Capability Layer
    ↓
OS API (Windows/Linux/macOS)
```

This architecture provides:
- **Permission enforcement** - Tools can only use capabilities declared in their manifest
- **Audit logging** - Every capability use is logged for security review
- **Sandboxing** - Filesystem paths are restricted, dangerous operations are blocked
- **Cross-platform compatibility** - Future Linux/macOS support without changing plugin code
- **Approval workflows** - High-risk operations require admin approval

---

## Capability Manifest

Every tool declares its required capabilities in the `#[tool]` macro:

```rust
#[tool(
    name = "restart_service",
    description = "Restart a Windows service",
    category = "system",
    risk_level = "high",
    requires_approval = true,
    capabilities = ["service.restart", "service.list"]
)]
async fn restart_service(ctx: &mut ToolContext) -> ToolResult {
    // Use capability layer
    let mut caps = ctx.capabilities();
    caps.service().restart("MyService").await?;
    Ok(ToolOutput::success("Service restarted"))
}
```

### Available Capabilities

#### Filesystem
- `filesystem.read` - Read files and directories
- `filesystem.write` - Write files to any location
- `filesystem.write.temp` - Write files to temp directory only
- `filesystem.delete` - Delete files

#### Registry (Windows only)
- `registry.read` - Read registry keys
- `registry.write` - Write registry keys
- `registry.delete` - Delete registry keys

#### Network
- `network.ping` - Ping network hosts
- `network.http` - Make HTTP/HTTPS requests
- `network.tcp` - Open TCP connections
- `network.dns` - Perform DNS lookups

#### Process
- `process.list` - List running processes
- `process.kill` - Terminate processes
- `process.start` - Start new processes
- `command.execute` - Execute arbitrary commands

#### Service (Windows only)
- `service.list` - List Windows services
- `service.start` - Start services
- `service.stop` - Stop services
- `service.restart` - Restart services

#### System
- `system.info` - Read system information
- `system.restart` - Restart the computer
- `system.shutdown` - Shutdown the computer
- `system.sleep` - Sleep/hibernate

#### Security
- `security.audit` - Audit security settings
- `security.modify` - Modify security settings

#### Display
- `display.message` - Show message dialogs
- `display.notification` - Show desktop notifications

---

## Risk Levels

Each capability has an associated risk level:

### Low Risk
- `filesystem.read`, `filesystem.write.temp`
- `registry.read`
- `process.list`, `service.list`
- `network.ping`, `network.dns`
- `system.info`, `security.audit`
- `display.message`, `display.notification`

**Policy**: Automatically granted at install time.

### Medium Risk
- `filesystem.write`, `registry.write`
- `process.start`, `service.start/stop/restart`
- `network.http`, `network.tcp`
- `command.execute` (some contexts)

**Policy**: Requires user approval at install time.

### High Risk
- `filesystem.delete`, `registry.delete`
- `process.kill`
- `security.modify`

**Policy**: Requires admin approval at install time.

### Critical Risk
- `system.restart`, `system.shutdown`, `system.sleep`

**Policy**: Requires admin approval at install time + confirmation dialog.

---

## Permission Prompts

When a user installs a plugin, they see a permission prompt:

```
┌─────────────────────────────────────────────────────────┐
│  Install: Gaming Optimization Plugin                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  This plugin requests the following permissions:         │
│                                                          │
│  ✓ Read system information                               │
│  ✓ Read files and directories                            │
│  ✓ Write temporary files                                 │
│  ✓ List running processes                                │
│  ⚠ Restart Windows services (requires approval)          │
│                                                          │
│  [Cancel]  [Install]                                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Capability Enforcement

The runtime enforces capabilities at multiple layers:

### 1. Install Time
```rust
let checker = CapabilityChecker::new();
let check = checker.check(&plugin.manifest.capabilities);

if !check.granted.is_empty() {
    // Show permission prompt
    prompt_user(&check);
}

if !check.denied.is_empty() {
    // Plugin cannot be installed
    return Err("Required capabilities denied");
}
```

### 2. Execution Time
```rust
impl FileSystemCapability {
    pub async fn read(&mut self, path: &str) -> Result<Vec<u8>> {
        // Check capability
        self.context.require(Capability::FilesystemRead)?;
        
        // Check path restrictions
        if !is_path_allowed(path) {
            return Err("Access denied");
        }
        
        // Perform operation
        tokio::fs::read(path).await
    }
}
```

### 3. Audit Time
```rust
// Every capability use is logged
self.audit_log.push(CapabilityAuditEntry {
    capability,
    action: CapabilityAction::Use,
    timestamp: chrono::Utc::now(),
    plugin_id: self.plugin_id.clone(),
    tool_name: self.tool_name.clone(),
});
```

---

## Path Sandboxing

The filesystem capability restricts access to dangerous paths:

### Blocked Paths
- `C:\Windows\System32`
- `C:\Program Files`
- `C:\Program Files (x86)`
- `C:\Users\All Users`
- `C:\Users\Default`

### Allowed Paths
- `C:\Users\<username>\*`
- `C:\Temp\*`
- `C:\ProgramData\AegisCloud\Plugins\<plugin-id>\*`

```rust
fn is_path_allowed(path: &str) -> bool {
    let path_lower = path.to_lowercase();
    
    let blocked = [
        "windows\\system32",
        "program files",
        "program files (x86)",
        "users\\all users",
        "users\\default",
    ];
    
    for blocked_path in blocked {
        if path_lower.contains(blocked_path) {
            return false;
        }
    }
    
    true
}
```

---

## Plugin Signing

All plugins must be signed before publication:

```
Developer signs plugin with their private key
    ↓
Marketplace verifies developer signature
    ↓
Marketplace signs plugin with marketplace key
    ↓
Integrity hash computed (manifest + binary)
    ↓
Plugin published with triple signature:
  - Developer signature
  - Marketplace signature
  - Integrity hash
```

### Verification at Runtime
```rust
// 1. Verify developer signature
verify_developer_signature(&plugin)?;

// 2. Verify marketplace signature
verify_marketplace_signature(&plugin)?;

// 3. Verify integrity hash
verify_integrity_hash(&plugin)?;

// 4. Check certificate revocation list
check_crl(&plugin.signer_certificate)?;
```

---

## SDK Versioning

The SDK uses semantic versioning to prevent breaking changes:

```rust
// Plugin built with SDK 1.2.3
pub sdk_version: "1.2.3"

// Runtime checks compatibility
if plugin.sdk_version.major() != current_sdk_version.major() {
    return Err("Incompatible SDK version");
}
```

### Version Compatibility
- **Major version changes** - Breaking changes, requires plugin recompilation
- **Minor version changes** - New features, backward compatible
- **Patch version changes** - Bug fixes, fully compatible

---

## Cross-Platform Support

The capability layer abstracts OS-specific APIs:

```rust
// Plugin code (cross-platform)
let services = ctx.capabilities().service().list().await?;

// Runtime implementation (OS-specific)
#[cfg(target_os = "windows")]
async fn list_services() -> Vec<ServiceInfo> {
    // Windows Service Control Manager API
}

#[cfg(target_os = "linux")]
async fn list_services() -> Vec<ServiceInfo> {
    // systemd API
}

#[cfg(target_os = "macos")]
async fn list_services() -> Vec<ServiceInfo> {
    // launchd API
}
```

---

## Security Model

### Defense in Depth

```
Layer 1: Plugin Signing
  - Developer signature
  - Marketplace signature
  - Integrity hash

Layer 2: Capability Declaration
  - Manifest-based permissions
  - User/admin approval
  - Risk level classification

Layer 3: Runtime Enforcement
  - Capability checking
  - Path sandboxing
  - Syscall filtering

Layer 4: Audit Logging
  - Every capability use logged
  - Anomaly detection
  - Security alerts

Layer 5: Resource Limits
  - Memory limits (100MB)
  - Execution time limits (30s)
  - File I/O limits
```

### Threat Mitigation

**Threat**: Malicious plugin tries to access system files
**Mitigation**: Capability denied + path sandboxing

**Threat**: Plugin tries to execute arbitrary commands
**Mitigation**: `command.execute` capability required + admin approval

**Threat**: Plugin tries to restart critical services
**Mitigation**: `service.restart` capability required + admin approval

**Threat**: Plugin tries to access registry
**Mitigation**: `registry.*` capabilities required + approval

---

## Best Practices

### 1. Request Minimum Capabilities
```rust
// ❌ Bad: Requesting too many capabilities
capabilities = ["filesystem.read", "filesystem.write", "filesystem.delete", ...]

// ✅ Good: Request only what you need
capabilities = ["filesystem.read"]
```

### 2. Use Temp Directory for Writes
```rust
// ❌ Bad: Writing to arbitrary locations
ctx.capabilities().filesystem().write("C:\\Windows\\file.txt", data).await?;

// ✅ Good: Use temp directory
ctx.capabilities().filesystem().write_temp("output.txt", data).await?;
```

### 3. Handle Capability Denied Errors
```rust
match ctx.capabilities().filesystem().read(path).await {
    Ok(data) => { /* success */ }
    Err(CapabilityLayerError::CapabilityDenied(_)) => {
        return Err(ToolError::PermissionDenied("Insufficient permissions"));
    }
    Err(e) => return Err(ToolError::ExecutionFailed(e.to_string())),
}
```

### 4. Document Required Capabilities
```rust
#[tool(
    name = "my_tool",
    description = "Does something useful",
    capabilities = ["filesystem.read"],  // Document why you need this
    // Requires filesystem.read to scan directories for files
)]
async fn my_tool(ctx: &mut ToolContext) -> ToolResult {
    // Implementation
}
```

---

## Future Enhancements

### Planned Capabilities
- `database.query` - Query local databases
- `docker.manage` - Manage Docker containers
- `vm.control` - Control virtual machines
- `gpu.monitor` - Monitor GPU performance

### Planned Features
- Dynamic capability grants (request at runtime)
- Capability inheritance (child tools inherit parent capabilities)
- Capability delegation (grant capabilities to other plugins)
- Capability expiration (time-limited grants)

---

## Related Documentation

- [Plugin SDK Reference](./sdk/PLUGIN_SDK_REFERENCE.md)
- [Plugin Developer Guide](./sdk/PLUGIN_DEVELOPER_GUIDE.md)
- [Security Model](./security/SECURITY_MODEL.md)
- [Marketplace API](./api/MARKETPLACE_API.md)
