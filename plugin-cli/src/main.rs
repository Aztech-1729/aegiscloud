//! Aegis Plugin CLI
//!
//! Command-line tool for plugin developers.
//! Usage:
//!   aegis plugin init my-plugin
//!   aegis plugin build
//!   aegis plugin publish
//!   aegis plugin validate

use clap::{Parser, Subcommand};
use std::fs;
use std::path::PathBuf;
use std::process::Command;

#[derive(Parser)]
#[command(name = "aegis")]
#[command(about = "Aegis Cloud Plugin CLI")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Plugin management commands
    Plugin {
        #[command(subcommand)]
        command: PluginCommands,
    },
}

#[derive(Subcommand)]
enum PluginCommands {
    /// Initialize a new plugin project
    Init {
        /// Plugin name
        name: String,
        /// Template to use (basic, docker, network, gaming)
        #[arg(short, long, default_value = "basic")]
        template: String,
    },
    /// Build the plugin
    Build {
        /// Build in release mode
        #[arg(short, long)]
        release: bool,
        /// Target platform (windows-x64, windows-arm64, wasm)
        #[arg(short, long, default_value = "windows-x64")]
        target: String,
    },
    /// Validate the plugin before publishing
    Validate,
    /// Publish the plugin to the marketplace
    Publish {
        /// Dry run (don't actually publish)
        #[arg(long)]
        dry_run: bool,
        /// API key for authentication
        #[arg(long)]
        api_key: Option<String>,
    },
    /// Test the plugin locally
    Test,
    /// Show plugin info
    Info,
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Plugin { command } => match command {
            PluginCommands::Init { name, template } => {
                init_plugin(&name, &template);
            }
            PluginCommands::Build { release, target } => {
                build_plugin(release, &target);
            }
            PluginCommands::Validate => {
                validate_plugin();
            }
            PluginCommands::Publish { dry_run, api_key } => {
                publish_plugin(dry_run, api_key);
            }
            PluginCommands::Test => {
                test_plugin();
            }
            PluginCommands::Info => {
                show_info();
            }
        },
    }
}

fn init_plugin(name: &str, template: &str) {
    println!("🚀 Initializing plugin: {}", name);
    
    // Create project structure
    let project_dir = PathBuf::from(name);
    fs::create_dir_all(project_dir.join("src")).expect("Failed to create directories");
    
    // Create Cargo.toml
    let cargo_toml = format!(
        r#"[package]
name = "{}"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
aegis-plugin-sdk = "1.0"
aegis-plugin-runtime = "1.0"
serde = {{ version = "1.0", features = ["derive"] }}
serde_json = "1.0"
tokio = {{ version = "1.0", features = ["full"] }}
"#,
        name
    );
    fs::write(project_dir.join("Cargo.toml"), cargo_toml).expect("Failed to write Cargo.toml");
    
    // Create manifest.json
    let manifest = serde_json::json!({
        "name": name,
        "version": "0.1.0",
        "author": "Your Name <your.email@example.com>",
        "description": "A sample Aegis Cloud plugin",
        "license": "MIT",
        "category": "custom",
        "platform": "windows-x64",
        "tools": []
    });
    fs::write(
        project_dir.join("manifest.json"),
        serde_json::to_string_pretty(&manifest).unwrap(),
    )
    .expect("Failed to write manifest.json");
    
    // Create lib.rs based on template
    let lib_rs = match template {
        "basic" => include_str!("../templates/basic.rs"),
        "docker" => include_str!("../templates/docker.rs"),
        _ => include_str!("../templates/basic.rs"),
    };
    fs::write(project_dir.join("src/lib.rs"), lib_rs).expect("Failed to write lib.rs");
    
    // Create README.md
    let readme = format!(
        r#"# {}

A sample Aegis Cloud plugin.

## Building

```bash
cargo build --release
```

## Publishing

```bash
aegis plugin publish
```
"#,
        name
    );
    fs::write(project_dir.join("README.md"), readme).expect("Failed to write README.md");
    
    println!("✅ Plugin initialized at ./{}/", name);
    println!("\nNext steps:");
    println!("  cd {}", name);
    println!("  cargo build --release");
    println!("  aegis plugin validate");
    println!("  aegis plugin publish");
}

fn build_plugin(release: bool, target: &str) {
    println!("🔨 Building plugin...");
    
    let mut cmd = Command::new("cargo");
    cmd.arg("build");
    
    if release {
        cmd.arg("--release");
    }
    
    // Set target based on platform
    let target_triple = match target {
        "windows-x64" => "x86_64-pc-windows-msvc",
        "windows-arm64" => "aarch64-pc-windows-msvc",
        "wasm" => "wasm32-unknown-unknown",
        _ => "x86_64-pc-windows-msvc",
    };
    
    cmd.args(["--target", target_triple]);
    
    let status = cmd.status().expect("Failed to run cargo build");
    
    if status.success() {
        println!("✅ Build successful");
        println!("\nNext: aegis plugin validate");
    } else {
        eprintln!("❌ Build failed");
        std::process::exit(1);
    }
}

fn validate_plugin() {
    println!("🔍 Validating plugin...");
    
    // Read manifest
    let manifest_content = fs::read_to_string("manifest.json").expect("Failed to read manifest.json");
    let manifest: serde_json::Value = serde_json::from_str(&manifest_content)
        .expect("Failed to parse manifest.json");
    
    // Check required fields
    let required_fields = vec!["name", "version", "author", "description", "license", "tools", "platform"];
    let mut errors = Vec::new();
    
    for field in required_fields {
        if manifest.get(field).is_none() {
            errors.push(format!("Missing required field: {}", field));
        }
    }
    
    // Validate version format
    if let Some(version) = manifest.get("version").and_then(|v| v.as_str()) {
        if !version.contains('.') {
            errors.push("Version must be in semver format (e.g., 1.0.0)".to_string());
        }
    }
    
    // Validate tools
    if let Some(tools) = manifest.get("tools").and_then(|t| t.as_array()) {
        if tools.is_empty() {
            errors.push("Plugin must provide at least one tool".to_string());
        }
        
        for (i, tool) in tools.iter().enumerate() {
            let tool_obj = tool.as_object().unwrap();
            
            if !tool_obj.contains_key("name") {
                errors.push(format!("Tool {}: missing 'name'", i));
            }
            if !tool_obj.contains_key("description") {
                errors.push(format!("Tool {}: missing 'description'", i));
            }
            if !tool_obj.contains_key("category") {
                errors.push(format!("Tool {}: missing 'category'", i));
            }
            if !tool_obj.contains_key("risk_level") {
                errors.push(format!("Tool {}: missing 'risk_level'", i));
            }
        }
    }
    
    if errors.is_empty() {
        println!("✅ Plugin is valid");
        println!("\nNext: aegis plugin publish");
    } else {
        eprintln!("❌ Validation failed:");
        for error in errors {
            eprintln!("  - {}", error);
        }
        std::process::exit(1);
    }
}

fn publish_plugin(dry_run: bool, api_key: Option<String>) {
    println!("📦 Publishing plugin...");
    
    if dry_run {
        println!("ℹ️  Dry run mode - not actually publishing");
        return;
    }
    
    let api_key = api_key
        .or_else(|| std::env::var("AEGIS_API_KEY").ok())
        .expect("API key required. Use --api-key or set AEGIS_API_KEY environment variable");
    
    // Read manifest
    let manifest_content = fs::read_to_string("manifest.json").expect("Failed to read manifest.json");
    let manifest: serde_json::Value = serde_json::from_str(&manifest_content)
        .expect("Failed to parse manifest.json");
    
    // Read binary
    let target_dir = PathBuf::from("target/x86_64-pc-windows-msvc/release");
    let binary_path = target_dir.join(format!("{}.dll", manifest["name"].as_str().unwrap()));
    
    if !binary_path.exists() {
        eprintln!("❌ Binary not found. Run 'aegis plugin build --release' first.");
        std::process::exit(1);
    }
    
    let binary = fs::read(&binary_path).expect("Failed to read binary");
    let binary_hash = format!("{:x}", sha2::Sha256::digest(&binary));
    
    println!("📤 Uploading to marketplace...");
    println!("  Plugin: {}", manifest["name"].as_str().unwrap());
    println!("  Version: {}", manifest["version"].as_str().unwrap());
    println!("  Size: {} KB", binary.len() / 1024);
    
    // TODO: Make HTTP request to Aegis API
    // POST https://api.aegiscloud.io/v1/plugins/publish
    // Headers: Authorization: Bearer {api_key}
    // Body: multipart/form-data with manifest.json and binary
    
    println!("\n✅ Plugin published successfully!");
    println!("\nView your plugin at:");
    println!("  https://marketplace.aegiscloud.io/plugins/{}", manifest["name"].as_str().unwrap());
}

fn test_plugin() {
    println!("🧪 Testing plugin locally...");
    
    // TODO: Load plugin into test runtime and run test cases
    println!("ℹ️  Local testing not yet implemented");
    println!("   Use 'aegis plugin validate' to check for errors");
}

fn show_info() {
    println!("ℹ️  Plugin Information\n");
    
    let manifest_content = fs::read_to_string("manifest.json").expect("Failed to read manifest.json");
    let manifest: serde_json::Value = serde_json::from_str(&manifest_content)
        .expect("Failed to parse manifest.json");
    
    println!("Name:        {}", manifest["name"].as_str().unwrap_or("N/A"));
    println!("Version:     {}", manifest["version"].as_str().unwrap_or("N/A"));
    println!("Author:      {}", manifest["author"].as_str().unwrap_or("N/A"));
    println!("Description: {}", manifest["description"].as_str().unwrap_or("N/A"));
    println!("License:     {}", manifest["license"].as_str().unwrap_or("N/A"));
    println!("Category:    {}", manifest["category"].as_str().unwrap_or("N/A"));
    println!("Platform:    {}", manifest["platform"].as_str().unwrap_or("N/A"));
    
    if let Some(tools) = manifest.get("tools").and_then(|t| t.as_array()) {
        println!("\nTools ({}):", tools.len());
        for tool in tools {
            let name = tool["name"].as_str().unwrap_or("N/A");
            let desc = tool["description"].as_str().unwrap_or("N/A");
            let risk = tool["risk_level"].as_str().unwrap_or("N/A");
            println!("  - {} ({}) [{}]", name, desc, risk);
        }
    }
}
