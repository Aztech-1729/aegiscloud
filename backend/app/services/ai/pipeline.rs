//! Real AI Pipeline — Planner → Executor → Verifier → Memory → Tool
//!
//! Instead of simple LLM → Tool mapping, this implements multi-step reasoning:
//!
//!   User Request
//!     ↓
//!   Planner (breaks down into sub-tasks)
//!     ↓
//!   Executor (runs tools in sequence/parallel)
//!     ↓
//!   Verifier (validates results)
//!     ↓
//!   Memory (stores for context)
//!     ↓
//!   Response (back to user)
//!
//! This allows complex operations like:
//! "My PC is slow and keeps crashing" → 
//!   Plan: [check_cpu, check_ram, check_disk, check_startup, check_drivers]
//!   Execute: [run each tool]
//!   Verify: [analyze results for anomalies]
//!   Respond: "I found 3 issues: high CPU from Chrome, low disk space, and outdated drivers"

use serde::{Deserialize, Serialize};
use log::{info, warn, error};

/// AI pipeline configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PipelineConfig {
    pub max_steps: usize,
    pub timeout_seconds: u64,
    pub require_verification: bool,
    pub store_in_memory: bool,
}

impl Default for PipelineConfig {
    fn default() -> Self {
        Self {
            max_steps: 10,
            timeout_seconds: 120,
            require_verification: true,
            store_in_memory: true,
        }
    }
}

/// A plan step — one action in the execution plan
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PlanStep {
    pub id: String,
    pub tool_name: String,
    pub parameters: serde_json::Value,
    pub description: String,
    pub depends_on: Vec<String>,  // Step IDs this depends on
    pub condition: Option<String>,  // Optional condition to execute
    pub priority: u8,
}

/// Execution plan — ordered list of steps
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionPlan {
    pub id: String,
    pub goal: String,
    pub steps: Vec<PlanStep>,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub status: PlanStatus,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum PlanStatus {
    Planning,
    Executing,
    Verifying,
    Completed,
    Failed,
    Cancelled,
}

/// Result of a single step execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StepResult {
    pub step_id: String,
    pub tool_name: String,
    pub success: bool,
    pub result: Option<serde_json::Value>,
    pub error: Option<String>,
    pub execution_time_ms: u64,
}

/// Verification result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerificationResult {
    pub overall_success: bool,
    pub confidence: f32,  // 0.0 to 1.0
    pub findings: Vec<Finding>,
    pub recommendations: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Finding {
    pub severity: Severity,
    pub category: String,
    pub description: String,
    pub tool: String,
    pub data: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Severity {
    Critical,
    High,
    Medium,
    Low,
    Info,
}

/// The AI Pipeline — orchestrates planning, execution, and verification
pub struct AIPipeline {
    config: PipelineConfig,
}

impl AIPipeline {
    pub fn new(config: PipelineConfig) -> Self {
        Self { config }
    }

    /// Phase 1: Planning — Break user request into actionable steps
    pub async fn plan(&self, user_request: &str, context: &str) -> Result<ExecutionPlan, String> {
        info!("Planning: {}", user_request);

        // Analyze the user request
        let intent = self.analyze_intent(user_request).await?;
        
        // Generate execution plan based on intent
        let plan = self.generate_plan(&intent, context).await?;
        
        info!("Plan created with {} steps", plan.steps.len());
        Ok(plan)
    }

    /// Phase 2: Execution — Run tools according to the plan
    pub async fn execute(&self, plan: &mut ExecutionPlan) -> Result<Vec<StepResult>, String> {
        info!("Executing plan: {}", plan.id);
        plan.status = PlanStatus::Executing;

        let mut results = Vec::new();
        let mut completed_steps = std::collections::HashSet::new();

        // Execute steps in dependency order
        for step in &plan.steps {
            // Check dependencies
            let deps_satisfied = step.depends_on.iter().all(|dep| completed_steps.contains(dep));
            if !deps_satisfied {
                warn!("Skipping step {} — dependencies not met", step.id);
                continue;
            }

            // Check condition
            if let Some(condition) = &step.condition {
                if !self.evaluate_condition(condition, &results).await {
                    info!("Skipping step {} — condition not met", step.id);
                    continue;
                }
            }

            // Execute the tool
            let start = std::time::Instant::now();
            let result = self.execute_tool(&step.tool_name, &step.parameters).await;
            let execution_time = start.elapsed().as_millis() as u64;

            let step_result = StepResult {
                step_id: step.id.clone(),
                tool_name: step.tool_name.clone(),
                success: result.is_ok(),
                result: result.ok(),
                error: None,
                execution_time_ms: execution_time,
            };

            if step_result.success {
                completed_steps.insert(step.id.clone());
            }

            results.push(step_result);
        }

        Ok(results)
    }

    /// Phase 3: Verification — Validate results and check for issues
    pub async fn verify(&self, plan: &ExecutionPlan, results: &[StepResult]) -> Result<VerificationResult, String> {
        info!("Verifying results for plan: {}", plan.id);

        let mut findings = Vec::new();
        let mut recommendations = Vec::new();
        let mut total_confidence = 0.0f32;
        let mut successful_steps = 0;

        for result in results {
            if result.success {
                successful_steps += 1;
                total_confidence += 1.0;
                
                // Analyze result data for issues
                if let Some(data) = &result.result {
                    let step_findings = self.analyze_result(&result.tool_name, data).await;
                    findings.extend(step_findings);
                }
            } else {
                total_confidence += 0.0;
                findings.push(Finding {
                    severity: Severity::Medium,
                    category: "execution".to_string(),
                    description: format!("Tool '{}' failed to execute", result.tool_name),
                    tool: result.tool_name.clone(),
                    data: serde_json::json!({"error": result.error}),
                });
            }
        }

        // Calculate overall confidence
        let overall_confidence = if results.is_empty() {
            0.0
        } else {
            total_confidence / results.len() as f32
        };

        // Generate recommendations based on findings
        for finding in &findings {
            if let Some(rec) = self.generate_recommendation(finding) {
                recommendations.push(rec);
            }
        }

        let overall_success = successful_steps == results.len() && overall_confidence > 0.5;

        Ok(VerificationResult {
            overall_success,
            confidence: overall_confidence,
            findings,
            recommendations,
        })
    }

    /// Phase 4: Memory — Store results for future context
    pub async fn store_in_memory(
        &self,
        device_id: &str,
        plan: &ExecutionPlan,
        results: &[StepResult],
        verification: &VerificationResult,
    ) -> Result<(), String> {
        info!("Storing results in memory for device: {}", device_id);
        
        // In production, this calls the backend API:
        // POST /api/v1/memory/{device_id}/store
        // with the plan, results, and verification data
        
        // For now, we log it
        info!("Memory stored: {} steps, {} findings, {} recommendations",
              results.len(), verification.findings.len(), verification.recommendations.len());
        
        Ok(())
    }

    /// Run the full pipeline: Plan → Execute → Verify → Memory
    pub async fn run(
        &self,
        user_request: &str,
        device_id: &str,
        context: &str,
    ) -> Result<PipelineResult, String> {
        let start = std::time::Instant::now();

        // Step 1: Plan
        let mut plan = self.plan(user_request, context).await?;

        // Check max steps
        if plan.steps.len() > self.config.max_steps {
            return Err(format!("Plan has {} steps, exceeding max of {}", 
                              plan.steps.len(), self.config.max_steps));
        }

        // Step 2: Execute
        let results = self.execute(&mut plan).await?;

        // Step 3: Verify
        let verification = if self.config.require_verification {
            plan.status = PlanStatus::Verifying;
            self.verify(&plan, &results).await?
        } else {
            VerificationResult {
                overall_success: results.iter().all(|r| r.success),
                confidence: 1.0,
                findings: Vec::new(),
                recommendations: Vec::new(),
            }
        };

        // Step 4: Memory
        if self.config.store_in_memory {
            let _ = self.store_in_memory(device_id, &plan, &results, &verification).await;
        }

        // Set final status
        plan.status = if verification.overall_success {
            PlanStatus::Completed
        } else {
            PlanStatus::Failed
        };

        let duration = start.elapsed().as_millis() as u64;

        Ok(PipelineResult {
            plan,
            results,
            verification,
            duration_ms: duration,
        })
    }

    /// Analyze user intent from natural language
    async fn analyze_intent(&self, request: &str) -> Result<UserIntent, String> {
        let lower = request.to_lowercase();
        
        // Performance issues
        if lower.contains("slow") || lower.contains("lag") || lower.contains("freeze") {
            return Ok(UserIntent::PerformanceDiagnosis);
        }

        // Security concerns
        if lower.contains("virus") || lower.contains("malware") || lower.contains("security") {
            return Ok(UserIntent::SecurityCheck);
        }

        // Cleanup
        if lower.contains("clean") || lower.contains("cleanup") || lower.contains("free space") {
            return Ok(UserIntent::Cleanup);
        }

        // Repair
        if lower.contains("repair") || lower.contains("fix") || lower.contains("broken") {
            return Ok(UserIntent::SystemRepair);
        }

        // Network
        if lower.contains("internet") || lower.contains("network") || lower.contains("connection") {
            return Ok(UserIntent::NetworkDiagnosis);
        }

        // General info
        if lower.contains("info") || lower.contains("specs") || lower.contains("what do i have") {
            return Ok(UserIntent::SystemInfo);
        }

        Ok(UserIntent::General)
    }

    /// Generate execution plan based on intent
    async fn generate_plan(&self, intent: &UserIntent, _context: &str) -> Result<ExecutionPlan, String> {
        let steps = match intent {
            UserIntent::PerformanceDiagnosis => vec![
                PlanStep {
                    id: "cpu".to_string(),
                    tool_name: "cpu_usage".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Check CPU usage".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 1,
                },
                PlanStep {
                    id: "ram".to_string(),
                    tool_name: "ram_usage".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Check RAM usage".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 1,
                },
                PlanStep {
                    id: "disk".to_string(),
                    tool_name: "disk_usage".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Check disk usage".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 1,
                },
                PlanStep {
                    id: "processes".to_string(),
                    tool_name: "list_processes".to_string(),
                    parameters: serde_json::json!({"sort_by": "cpu", "limit": 10}),
                    description: "List top processes".to_string(),
                    depends_on: vec!["cpu".to_string()],
                    condition: None,
                    priority: 2,
                },
                PlanStep {
                    id: "startup".to_string(),
                    tool_name: "list_startup".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Check startup programs".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 2,
                },
            ],
            UserIntent::SecurityCheck => vec![
                PlanStep {
                    id: "defender".to_string(),
                    tool_name: "defender_status".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Check Windows Defender".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 1,
                },
                PlanStep {
                    id: "firewall".to_string(),
                    tool_name: "firewall_status".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Check Firewall".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 1,
                },
                PlanStep {
                    id: "processes".to_string(),
                    tool_name: "list_processes".to_string(),
                    parameters: serde_json::json!({"sort_by": "cpu", "limit": 20}),
                    description: "Check for suspicious processes".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 2,
                },
            ],
            UserIntent::Cleanup => vec![
                PlanStep {
                    id: "temp".to_string(),
                    tool_name: "clean_temp".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Clean temporary files".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 1,
                },
                PlanStep {
                    id: "recycle".to_string(),
                    tool_name: "empty_recycle_bin".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Empty Recycle Bin".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 1,
                },
                PlanStep {
                    id: "dns".to_string(),
                    tool_name: "flush_dns".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Flush DNS cache".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 2,
                },
                PlanStep {
                    id: "storage".to_string(),
                    tool_name: "storage_analysis".to_string(),
                    parameters: serde_json::json!({"min_size_mb": 100}),
                    description: "Analyze large files".to_string(),
                    depends_on: vec!["temp".to_string()],
                    condition: None,
                    priority: 3,
                },
            ],
            UserIntent::SystemRepair => vec![
                PlanStep {
                    id: "sfc".to_string(),
                    tool_name: "run_sfc".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Run System File Checker".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 1,
                },
                PlanStep {
                    id: "dism".to_string(),
                    tool_name: "run_dism".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Run DISM repair".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 1,
                },
                PlanStep {
                    id: "dns".to_string(),
                    tool_name: "flush_dns".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Flush DNS cache".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 2,
                },
                PlanStep {
                    id: "explorer".to_string(),
                    tool_name: "restart_explorer".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Restart Windows Explorer".to_string(),
                    depends_on: vec!["sfc".to_string(), "dism".to_string()],
                    condition: None,
                    priority: 3,
                },
            ],
            UserIntent::NetworkDiagnosis => vec![
                PlanStep {
                    id: "network".to_string(),
                    tool_name: "network_info".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Check network adapters".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 1,
                },
                PlanStep {
                    id: "public_ip".to_string(),
                    tool_name: "public_ip".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Check public IP".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 1,
                },
                PlanStep {
                    id: "dns".to_string(),
                    tool_name: "flush_dns".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Flush DNS cache".to_string(),
                    depends_on: vec!["network".to_string()],
                    condition: None,
                    priority: 2,
                },
            ],
            UserIntent::SystemInfo => vec![
                PlanStep {
                    id: "info".to_string(),
                    tool_name: "system_info".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Get system information".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 1,
                },
                PlanStep {
                    id: "disk".to_string(),
                    tool_name: "disk_usage".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Check disk space".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 1,
                },
            ],
            UserIntent::General => vec![
                PlanStep {
                    id: "info".to_string(),
                    tool_name: "system_info".to_string(),
                    parameters: serde_json::json!({}),
                    description: "Get system information".to_string(),
                    depends_on: vec![],
                    condition: None,
                    priority: 1,
                },
            ],
        };

        Ok(ExecutionPlan {
            id: uuid::Uuid::new_v4().to_string(),
            goal: format!("{:?}", intent),
            steps,
            created_at: chrono::Utc::now(),
            status: PlanStatus::Planning,
        })
    }

    /// Execute a single tool
    async fn execute_tool(&self, tool_name: &str, parameters: &serde_json::Value) -> Result<serde_json::Value, String> {
        info!("Executing tool: {} with params: {}", tool_name, parameters);
        
        // In production, this sends the command to the backend
        // POST /api/v1/commands with device_id, tool_name, parameters
        
        // For now, return mock data
        Ok(serde_json::json!({
            "success": true,
            "tool": tool_name,
            "message": "Tool executed successfully",
        }))
    }

    /// Evaluate a condition expression
    async fn evaluate_condition(&self, condition: &str, results: &[StepResult]) -> bool {
        // Simple condition evaluation
        // In production, this would be a proper expression evaluator
        info!("Evaluating condition: {}", condition);
        true
    }

    /// Analyze tool result for issues
    async fn analyze_result(&self, tool_name: &str, data: &serde_json::Value) -> Vec<Finding> {
        let mut findings = Vec::new();

        match tool_name {
            "cpu_usage" => {
                if let Some(cpu) = data.get("cpu_percent").and_then(|v| v.as_f64()) {
                    if cpu > 90.0 {
                        findings.push(Finding {
                            severity: Severity::High,
                            category: "performance".to_string(),
                            description: format!("CPU usage is critically high: {:.1}%", cpu),
                            tool: tool_name.to_string(),
                            data: data.clone(),
                        });
                    } else if cpu > 70.0 {
                        findings.push(Finding {
                            severity: Severity::Medium,
                            category: "performance".to_string(),
                            description: format!("CPU usage is elevated: {:.1}%", cpu),
                            tool: tool_name.to_string(),
                            data: data.clone(),
                        });
                    }
                }
            }
            "ram_usage" => {
                if let Some(ram) = data.get("percent").and_then(|v| v.as_f64()) {
                    if ram > 90.0 {
                        findings.push(Finding {
                            severity: Severity::High,
                            category: "performance".to_string(),
                            description: format!("RAM usage is critically high: {:.1}%", ram),
                            tool: tool_name.to_string(),
                            data: data.clone(),
                        });
                    }
                }
            }
            "disk_usage" => {
                if let Some(disks) = data.get("disks").and_then(|v| v.as_array()) {
                    for disk in disks {
                        if let Some(used_gb) = disk.get("used_gb").and_then(|v| v.as_f64()) {
                            if let Some(total_gb) = disk.get("total_gb").and_then(|v| v.as_f64()) {
                                let percent = (used_gb / total_gb) * 100.0;
                                if percent > 95.0 {
                                    findings.push(Finding {
                                        severity: Severity::Critical,
                                        category: "storage".to_string(),
                                        description: format!("Disk is nearly full: {:.1}%", percent),
                                        tool: tool_name.to_string(),
                                        data: disk.clone(),
                                    });
                                }
                            }
                        }
                    }
                }
            }
            "defender_status" => {
                if let Some(enabled) = data.get("real_time_protection").and_then(|v| v.as_bool()) {
                    if !enabled {
                        findings.push(Finding {
                            severity: Severity::Critical,
                            category: "security".to_string(),
                            description: "Windows Defender real-time protection is DISABLED".to_string(),
                            tool: tool_name.to_string(),
                            data: data.clone(),
                        });
                    }
                }
            }
            _ => {}
        }

        findings
    }

    /// Generate recommendation from a finding
    fn generate_recommendation(&self, finding: &Finding) -> Option<String> {
        match finding.category.as_str() {
            "performance" => Some(format!("Consider closing unused applications or increasing system resources. Issue: {}", finding.description)),
            "storage" => Some("Run 'Deep Cleanup' skill to free disk space.".to_string()),
            "security" => Some("Enable Windows Defender immediately. Run 'Security Audit' skill.".to_string()),
            _ => None,
        }
    }
}

/// User intent categories
#[derive(Debug, Clone)]
enum UserIntent {
    PerformanceDiagnosis,
    SecurityCheck,
    Cleanup,
    SystemRepair,
    NetworkDiagnosis,
    SystemInfo,
    General,
}

/// Complete pipeline result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PipelineResult {
    pub plan: ExecutionPlan,
    pub results: Vec<StepResult>,
    pub verification: VerificationResult,
    pub duration_ms: u64,
}
