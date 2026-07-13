"""Plugin SDK — Developer experience for creating Aegis plugins.

Developer workflow:
    cargo new aegis-my-plugin --lib
    ↓
    Add dependency: aegis-plugin-sdk = "1.0"
    ↓
    Write tools with #[tool] macro
    ↓
    cargo build --release
    ↓
    aegis plugin publish
    ↓
    Available in marketplace

Example Plugin:

```rust
use aegis_plugin_sdk::*;

#[plugin(
    name = "Docker Manager",
    version = "1.0.0",
    author = "developer@example.com",
    description = "Manage Docker containers"
)]
pub struct DockerPlugin;

#[tool(
    name = "docker_list",
    description = "List running Docker containers",
    risk_level = "low",
    input = {},
    output = { containers: Vec<Container> }
)]
async fn list_containers() -> ToolResult {
    let output = Command::new("docker")
        .args(["ps", "--format", "json"])
        .output()
        .await?;
    
    let containers: Vec<Container> = serde_json::from_slice(&output.stdout)?;
    
    Ok(ToolResult::success(json!({ "containers": containers })))
}

#[tool(
    name = "docker_stop",
    description = "Stop a Docker container",
    risk_level = "high",
    requires_approval = true,
    input = { container_id: String },
    output = { success: bool }
)]
async fn stop_container(container_id: String) -> ToolResult {
    let output = Command::new("docker")
        .args(["stop", &container_id])
        .output()
        .await?;
    
    Ok(ToolResult::success(json!({ 
        "success": output.status.success() 
    })))
}
```
"""


# ============= PLUGIN MANIFEST SCHEMA =============

PLUGIN_MANIFEST_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["name", "version", "author", "description", "tools"],
    "properties": {
        "name": {"type": "string", "description": "Plugin display name"},
        "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
        "author": {"type": "string", "description": "Author name or email"},
        "description": {"type": "string", "maxLength": 500},
        "category": {
            "type": "string",
            "enum": ["hardware", "developer", "virtualization", "gaming", "network", "maintenance", "diagnostic", "security", "custom"]
        },
        "icon": {"type": "string", "maxLength": 10},
        "tools": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "description", "input_schema", "output_schema"],
                "properties": {
                    "name": {"type": "string", "pattern": "^[a-z][a-z0-9_]*$"},
                    "description": {"type": "string"},
                    "risk_level": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "default": "medium"
                    },
                    "requires_approval": {"type": "boolean", "default": False},
                    "input_schema": {"type": "object"},
                    "output_schema": {"type": "object"},
                    "examples": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "input": {"type": "object"},
                                "output": {"type": "object"},
                                "description": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        "permissions": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["network", "filesystem", "registry", "process", "service", "gpu", "docker", "wsl"]
            }
        },
        "platforms": {
            "type": "array",
            "items": {"type": "string", "enum": ["windows-x64", "windows-arm64"]},
            "default": ["windows-x64"]
        },
        "min_agent_version": {"type": "string"},
        "max_agent_version": {"type": "string"},
        "homepage": {"type": "string", "format": "uri"},
        "repository": {"type": "string", "format": "uri"},
        "license": {"type": "string"},
    }
}


# ============= PLUGIN REVIEW PROCESS =============

REVIEW_CHECKLIST = [
    {
        "id": "manifest_valid",
        "name": "Valid Manifest",
        "description": "Plugin manifest matches schema",
        "automated": True,
    },
    {
        "id": "no_arbitrary_commands",
        "name": "No Arbitrary Commands",
        "description": "Plugin does not execute arbitrary shell commands",
        "automated": True,
    },
    {
        "id": "no_filesystem_writes",
        "name": "Restricted Filesystem",
        "description": "Plugin only reads/writes to allowed directories",
        "automated": True,
    },
    {
        "id": "no_network_exfil",
        "name": "No Data Exfiltration",
        "description": "Plugin does not send data to external servers",
        "automated": True,
    },
    {
        "id": "input_validation",
        "name": "Input Validation",
        "description": "All inputs are validated against schema",
        "automated": True,
    },
    {
        "id": "error_handling",
        "name": "Error Handling",
        "description": "Plugin handles errors gracefully",
        "automated": False,
    },
    {
        "id": "performance",
        "name": "Performance",
        "description": "Plugin does not consume excessive resources",
        "automated": False,
    },
    {
        "id": "documentation",
        "name": "Documentation",
        "description": "Plugin has clear documentation and examples",
        "automated": False,
    },
]


# ============= PLUGIN CLI COMMANDS =============

CLI_COMMANDS = {
    "aegis plugin init": {
        "description": "Initialize a new plugin project",
        "args": ["name", "--template"],
        "example": "aegis plugin init my-docker-plugin --template docker",
    },
    "aegis plugin build": {
        "description": "Build the plugin for distribution",
        "args": ["--release", "--target"],
        "example": "aegis plugin build --release --target windows-x64",
    },
    "aegis plugin test": {
        "description": "Run plugin tests",
        "args": ["--verbose"],
        "example": "aegis plugin test --verbose",
    },
    "aegis plugin publish": {
        "description": "Publish plugin to marketplace",
        "args": ["--dry-run"],
        "example": "aegis plugin publish",
    },
    "aegis plugin validate": {
        "description": "Validate plugin manifest and binaries",
        "args": [],
        "example": "aegis plugin validate",
    },
}


# ============= PLUGIN TEMPLATES =============

PLUGIN_TEMPLATES = {
    "basic": {
        "description": "Basic plugin with one tool",
        "files": {
            "Cargo.toml": """
[package]
name = "aegis-{name}"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
aegis-plugin-sdk = "1.0"
serde = {{ version = "1.0", features = ["derive"] }}
serde_json = "1.0"
tokio = {{ version = "1.0", features = ["full"] }}
""",
            "src/lib.rs": """
use aegis_plugin_sdk::*;

#[plugin(
    name = "{name}",
    version = "0.1.0",
    author = "Your Name",
    description = "A custom Aegis Cloud plugin"
)]
pub struct {Name}Plugin;

#[tool(
    name = "{name}_hello",
    description = "Say hello",
    risk_level = "low",
    input = {{ "name": "String" }},
    output = {{ "message": "String" }}
)]
async fn hello(name: String) -> ToolResult {{
    Ok(ToolResult::success(json!({{
        "message": format!("Hello, {{}}!", name)
    }})))
}}
""",
            "manifest.json": """
{{
    "name": "{name}",
    "version": "0.1.0",
    "author": "Your Name",
    "description": "A custom Aegis Cloud plugin",
    "category": "custom",
    "tools": [
        {{
            "name": "{name}_hello",
            "description": "Say hello",
            "risk_level": "low",
            "input_schema": {{
                "type": "object",
                "properties": {{
                    "name": {{ "type": "string" }}
                }},
                "required": ["name"]
            }},
            "output_schema": {{
                "type": "object",
                "properties": {{
                    "message": {{ "type": "string" }}
                }}
            }}
        }}
    ]
}}
""",
        }
    },
    "docker": {
        "description": "Docker management plugin",
        "files": {
            "Cargo.toml": """
[package]
name = "aegis-docker-plugin"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
aegis-plugin-sdk = "1.0"
serde = {{ version = "1.0", features = ["derive"] }}
serde_json = "1.0"
tokio = {{ version = "1.0", features = ["full", "process"] }}
""",
        }
    },
}
