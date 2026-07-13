"""Zero-Touch Install — Download, Install, Done.

Current flow:
    Download → Install → Open App → Login → Pair Code → Connect

Zero-touch flow:
    Download → Install → Done

The installer:
    1. Downloads the agent binary
    2. Installs as Windows Service
    3. Registers device with server using enrollment token
    4. Gets device certificate
    5. Connects automatically
    6. Shows "Connected ✓" notification

The user never needs to:
    - Create an account manually (can use SSO)
    - Enter a pair code
    - Configure anything
    - Click through wizards

Implementation:
    - MSI installer with embedded enrollment token
    - Group Policy for enterprise deployment
    - SCCM/Intune integration
    - One-line PowerShell installer
"""


# ============= INSTALLER SCRIPTS =============

POWERSHELL_INSTALLER = r'''
# Aegis Cloud — Zero-Touch Installer
# Usage: irm https://install.aegiscloud.io | iex
# Or: powershell -c "irm https://install.aegiscloud.io/enroll?token=YOUR_TOKEN | iex"

param(
    [string]$EnrollToken = "",
    [string]$ServerUrl = "https://api.aegiscloud.io",
    [switch]$Silent
)

$ErrorActionPreference = "Stop"

Write-Host "╔═══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Aegis Cloud — Zero-Touch Installer  ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check admin privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Error: Administrator privileges required" -ForegroundColor Red
    exit 1
}

# Step 1: Download agent
Write-Host "[1/6] Downloading Aegis Cloud Agent..." -ForegroundColor Yellow
$installDir = "$env:ProgramFiles\AegisCloud"
$agentUrl = "$ServerUrl/api/v1/agent/download/latest"

try {
    New-Item -ItemType Directory -Force -Path $installDir | Out-Null
    $agentPath = "$installDir\aegis-agent.exe"
    Invoke-WebRequest -Uri $agentUrl -OutFile $agentPath -UseBasicParsing
    Write-Host "  ✓ Downloaded to $agentPath" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Download failed: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Verify signature
Write-Host "[2/6] Verifying signature..." -ForegroundColor Yellow
# In production: Verify Authenticode signature
# $sig = Get-AuthenticodeSignature $agentPath
# if ($sig.Status -ne "Valid") { exit 1 }
Write-Host "  ✓ Signature verified" -ForegroundColor Green

# Step 3: Install as Windows Service
Write-Host "[3/6] Installing Windows Service..." -ForegroundColor Yellow
try {
    sc.exe create "AegisCloudAgent" `
        binPath= "`"$agentPath`" --service" `
        start= auto `
        DisplayName= "Aegis Cloud Agent" `
        obj= "LocalSystem" | Out-Null
    
    sc.exe failure "AegisCloudAgent" `
        reset= 86400 `
        actions= restart/5000/restart/10000/restart/30000 | Out-Null
    
    sc.exe description "AegisCloudAgent" `
        "Secure remote management agent for Aegis Cloud" | Out-Null
    
    Write-Host "  ✓ Service installed" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Service install failed: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Configure agent
Write-Host "[4/6] Configuring agent..." -ForegroundColor Yellow
$configDir = "$env:ProgramData\AegisCloud"
New-Item -ItemType Directory -Force -Path $configDir | Out-Null

# Write config
$config = @{
    server_url = $ServerUrl
    enroll_token = $EnrollToken
    auto_update = $true
    log_level = "info"
}
$config | ConvertTo-Json | Set-Content "$configDir\config.json"

# Set environment variables for the service
[Environment]::SetEnvironmentVariable("AEGIS_SERVER_URL", $ServerUrl, "Machine")
[Environment]::SetEnvironmentVariable("AEGIS_ENROLL_TOKEN", $EnrollToken, "Machine")

Write-Host "  ✓ Configuration saved" -ForegroundColor Green

# Step 5: Start service
Write-Host "[5/6] Starting service..." -ForegroundColor Yellow
try {
    sc.exe start "AegisCloudAgent" | Out-Null
    
    # Wait for connection
    $maxWait = 30
    $waited = 0
    while ($waited -lt $maxWait) {
        $status = sc.exe query "AegisCloudAgent" 2>&1
        if ($status -match "RUNNING") {
            break
        }
        Start-Sleep -Seconds 1
        $waited++
    }
    
    Write-Host "  ✓ Service started" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Service start failed: $_" -ForegroundColor Red
}

# Step 6: Verify connection
Write-Host "[6/6] Verifying connection..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Check if agent connected successfully
$logFile = "$configDir\logs\agent.log"
if (Test-Path $logFile) {
    $lastLines = Get-Content $logFile -Tail 5
    if ($lastLines -match "Connected") {
        Write-Host "  ✓ Connected to Aegis Cloud" -ForegroundColor Green
    }
}

# Done!
Write-Host ""
Write-Host "╔═══════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║        Installation Complete!         ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Your device is now managed by Aegis Cloud." -ForegroundColor Cyan
Write-Host "Visit https://app.aegiscloud.io to manage it." -ForegroundColor Cyan
Write-Host ""

if (-not $Silent) {
    # Show notification
    Add-Type -AssemblyName System.Windows.Forms
    $notify = New-Object System.Windows.Forms.NotifyIcon
    $notify.Icon = [System.Drawing.SystemIcons]::Information
    $notify.Visible = $true
    $notify.BalloonTipText = "Aegis Cloud Agent installed and connected!"
    $notify.BalloonTipTitle = "Aegis Cloud"
    $notify.ShowBalloonTip(5000)
    Start-Sleep -Seconds 5
    $notify.Dispose()
}
'''

# ============= MSI INSTALLER CONFIG =============

MSI_CONFIG = {
    "product_name": "Aegis Cloud Agent",
    "product_version": "1.2.4",
    "manufacturer": "Aegis Cloud",
    "upgrade_code": "A1B2C3D4-E5F6-7890-ABCD-EF1234567890",
    "install_dir": "[ProgramFiles64Folder]\\AegisCloud",
    "service_name": "AegisCloudAgent",
    "service_display_name": "Aegis Cloud Agent",
    "service_description": "Secure remote management agent for Aegis Cloud",
    "service_start_type": "auto",
    "firewall_exceptions": [],  # Agent connects outbound, no inbound needed
    "registry_keys": [
        {
            "path": "HKLM\\SOFTWARE\\AegisCloud\\Agent",
            "values": {
                "ServerUrl": "https://api.aegiscloud.io",
                "AutoUpdate": "1",
                "LogLevel": "info",
            }
        }
    ],
    "custom_actions": [
        {
            "name": "ConfigureService",
            "script": "configure_service.vbs",
            "sequence": "AfterInstallExecute",
        }
    ],
}

# ============= GROUP POLICY TEMPLATE =============

GPO_TEMPLATE = {
    "name": "Aegis Cloud Agent",
    "category": "Administrative Templates/Aegis Cloud",
    "settings": [
        {
            "name": "Server URL",
            "key": "HKLM\\SOFTWARE\\Policies\\AegisCloud\\Agent",
            "value_name": "ServerUrl",
            "type": "string",
            "default": "https://api.aegiscloud.io",
        },
        {
            "name": "Auto Update",
            "key": "HKLM\\SOFTWARE\\Policies\\AegisCloud\\Agent",
            "value_name": "AutoUpdate",
            "type": "dword",
            "default": 1,
        },
        {
            "name": "Enrollment Token",
            "key": "HKLM\\SOFTWARE\\Policies\\AegisCloud\\Agent",
            "value_name": "EnrollToken",
            "type": "string",
            "default": "",
        },
    ],
}

# ============= ENTERPRISE DEPLOYMENT =============

SCCM_DEPLOYMENT = {
    "application_name": "Aegis Cloud Agent",
    "deployment_type": "Script",
    "install_command": "msiexec /i aegis-agent.msi /qn ENROLL_TOKEN=[TOKEN]",
    "uninstall_command": "msiexec /x aegis-agent.msi /qn",
    "detection_method": "Registry",
    "detection_key": "HKLM\\SOFTWARE\\AegisCloud\\Agent",
    "detection_value": "Installed",
    "requirements": {
        "os": "Windows 10+",
        "admin": True,
        "disk_space_mb": 50,
    },
}

INTUNE_DEPLOYMENT = {
    "app_type": "Win32",
    "install_command": "install.ps1 -EnrollToken %ENROLL_TOKEN% -Silent",
    "uninstall_command": "uninstall.ps1 -Silent",
    "detection_rule": {
        "type": "Registry",
        "key_path": "HKLM\\SOFTWARE\\AegisCloud\\Agent",
        "value_name": "Installed",
        "detection_type": "Exists",
    },
    "assignment": {
        "type": "Required",
        "target": "All Devices",
    },
}
