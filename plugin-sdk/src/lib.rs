//! Aegis Cloud Plugin SDK
//! 
//! Build powerful tools for Aegis Cloud with Rust.
//! 
//! # Example
//! 
//! ```rust
//! use aegis_plugin_sdk::prelude::*;
//! 
//! #[tool(
//!     name = "list_processes",
//!     description = "List all running processes",
//!     category = "system",
//!     risk_level = "low",
//!     capabilities = ["process.list"]
//! )]
//! async fn list_processes(ctx: &mut ToolContext) -> ToolResult {
//!     let processes = ctx.capabilities().process().list().await?;
//!     Ok(ToolOutput::success(processes))
//! }
//! ```

use proc_macro::TokenStream;
use quote::{quote, format_ident};
use syn::{parse_macro_input, ItemFn, Lit, Meta, NestedMeta};

/// The #[tool] attribute macro for defining plugin tools
/// 
/// # Attributes
/// 
/// - `name` (required): Unique tool name (snake_case)
/// - `description` (required): Human-readable description
/// - `category` (required): Tool category (system, process, file, network, security, maintenance)
/// - `risk_level` (required): Risk level (low, medium, high, critical)
/// - `capabilities` (optional): Array of required capabilities
/// - `timeout` (optional): Execution timeout in seconds (default: 30)
/// - `requires_approval` (optional): Requires admin approval (default: false)
#[proc_macro_attribute]
pub fn tool(attr: TokenStream, item: TokenStream) -> TokenStream {
    let args = parse_macro_input!(attr as AttributeArgs);
    let input = parse_macro_input!(item as ItemFn);
    
    // Parse attributes
    let mut name = String::new();
    let mut description = String::new();
    let mut category = String::new();
    let mut risk_level = String::new();
    let mut capabilities: Vec<String> = Vec::new();
    let mut timeout = 30u64;
    let mut requires_approval = false;
    
    for arg in args {
        if let NestedMeta::Meta(Meta::NameValue(nv)) = arg {
            let key = nv.path.get_ident().map(|i| i.to_string()).unwrap_or_default();
            
            match key.as_str() {
                "name" => {
                    if let Lit::Str(lit) = nv.lit {
                        name = lit.value();
                    }
                }
                "description" => {
                    if let Lit::Str(lit) = nv.lit {
                        description = lit.value();
                    }
                }
                "category" => {
                    if let Lit::Str(lit) = nv.lit {
                        category = lit.value();
                    }
                }
                "risk_level" => {
                    if let Lit::Str(lit) = nv.lit {
                        risk_level = lit.value();
                    }
                }
                "capabilities" => {
                    if let Lit::Array(arr) = nv.lit {
                        for elem in arr.elems {
                            if let syn::Expr::Lit(expr_lit) = elem {
                                if let Lit::Str(lit) = expr_lit.lit {
                                    capabilities.push(lit.value());
                                }
                            }
                        }
                    }
                }
                "timeout" => {
                    if let Lit::Int(lit) = nv.lit {
                        timeout = lit.base10_parse().unwrap_or(30);
                    }
                }
                "requires_approval" => {
                    if let Lit::Bool(lit) = nv.lit {
                        requires_approval = lit.value;
                    }
                }
                _ => {}
            }
        }
    }
    
    // Validate required fields
    if name.is_empty() {
        panic!("Tool must have a 'name' attribute");
    }
    if description.is_empty() {
        panic!("Tool must have a 'description' attribute");
    }
    if category.is_empty() {
        panic!("Tool must have a 'category' attribute");
    }
    if risk_level.is_empty() {
        panic!("Tool must have a 'risk_level' attribute");
    }
    
    // Generate tool name identifier
    let tool_name_ident = format_ident!("{}", name);
    let fn_name = &input.sig.ident;
    let fn_inputs = &input.sig.inputs;
    let fn_output = &input.sig.output;
    let fn_body = &input.block;
    
    // Generate capability requirements
    let capability_reqs: Vec<_> = capabilities.iter().map(|cap| {
        let cap_ident = match cap.as_str() {
            "filesystem.read" => quote! { Capability::FilesystemRead },
            "filesystem.write" => quote! { Capability::FilesystemWrite },
            "filesystem.write.temp" => quote! { Capability::FilesystemWriteTemp },
            "filesystem.delete" => quote! { Capability::FilesystemDelete },
            "registry.read" => quote! { Capability::RegistryRead },
            "registry.write" => quote! { Capability::RegistryWrite },
            "registry.delete" => quote! { Capability::RegistryDelete },
            "process.list" => quote! { Capability::ProcessList },
            "process.kill" => quote! { Capability::ProcessKill },
            "process.start" => quote! { Capability::ProcessStart },
            "service.list" => quote! { Capability::ServiceList },
            "service.start" => quote! { Capability::ServiceStart },
            "service.stop" => quote! { Capability::ServiceStop },
            "service.restart" => quote! { Capability::ServiceRestart },
            "network.ping" => quote! { Capability::NetworkPing },
            "network.http" => quote! { Capability::NetworkHttp },
            "network.tcp" => quote! { Capability::NetworkTcp },
            "network.dns" => quote! { Capability::NetworkDns },
            "system.info" => quote! { Capability::SystemInfo },
            "system.restart" => quote! { Capability::SystemRestart },
            "system.shutdown" => quote! { Capability::SystemShutdown },
            "system.sleep" => quote! { Capability::SystemSleep },
            "security.audit" => quote! { Capability::SecurityAudit },
            "security.modify" => quote! { Capability::SecurityModify },
            "command.execute" => quote! { Capability::CommandExecute },
            "script.execute" => quote! { Capability::ScriptExecute },
            "display.message" => quote! { Capability::DisplayMessage },
            "display.notification" => quote! { Capability::DisplayNotification },
            _ => panic!("Unknown capability: {}", cap),
        };
        quote! { #cap_ident }
    }).collect();
    
    // Generate the expanded code
    let expanded = quote! {
        use aegis_plugin_runtime::capabilities::{Capability, CapabilityManifest};
        
        // Original function
        async fn #fn_name(#fn_inputs) #fn_output #fn_body
        
        // Tool registration struct
        pub struct #tool_name_ident;
        
        #[aegis_plugin_sdk::async_trait]
        impl aegis_plugin_runtime::Tool for #tool_name_ident {
            fn metadata(&self) -> aegis_plugin_runtime::ToolMetadata {
                let mut manifest = CapabilityManifest::new();
                #(manifest.require(#capability_reqs);)*
                
                aegis_plugin_runtime::ToolMetadata {
                    name: #name.to_string(),
                    description: #description.to_string(),
                    category: #category.to_string(),
                    risk_level: #risk_level.to_string(),
                    capabilities: manifest,
                    requires_approval: #requires_approval,
                    timeout: #timeout,
                }
            }
            
            async fn execute(&self, params: serde_json::Value) -> aegis_plugin_runtime::ToolResult {
                // Create capability context from manifest
                let granted = self.metadata().capabilities.required.clone();
                let context = aegis_plugin_runtime::CapabilityContext::new(
                    granted,
                    stringify!(#tool_name_ident).to_string(),
                    #name.to_string()
                );
                
                // Create tool context with capability layer
                let mut ctx = aegis_plugin_runtime::ToolContext::new(context);
                
                // Call the tool function
                #fn_name(&mut ctx, params).await
            }
        }
        
        // Auto-register the tool
        aegis_plugin_runtime::inventory::submit! {
            Box::new(#tool_name_ident) as Box<dyn aegis_plugin_runtime::Tool>
        }
    };
    
    TokenStream::from(expanded)
}

/// Parse macro arguments
struct AttributeArgs(Vec<NestedMeta>);

impl syn::parse::Parse for AttributeArgs {
    fn parse(input: syn::parse::ParseStream) -> syn::Result<Self> {
        let mut args = Vec::new();
        
        while !input.is_empty() {
            args.push(input.parse()?);
            if !input.is_empty() {
                input.parse::<syn::Token![,]>()?;
            }
        }
        
        Ok(AttributeArgs(args))
    }
}

impl IntoIterator for AttributeArgs {
    type Item = NestedMeta;
    type IntoIter = std::vec::IntoIter<Self::Item>;
    
    fn into_iter(self) -> Self::IntoIter {
        self.0.into_iter()
    }
}

/// Prelude for convenient imports
pub mod prelude {
    pub use crate::tool;
    pub use aegis_plugin_runtime::{
        Tool, ToolMetadata, ToolOutput, ToolResult, ToolContext,
        CapabilityLayer, CapabilityLayerError,
    };
    pub use aegis_plugin_runtime::capabilities::{
        Capability, CapabilityManifest, CapabilityContext,
        CapabilityError, RiskLevel,
    };
    pub use serde_json;
    pub use async_trait::async_trait;
}
