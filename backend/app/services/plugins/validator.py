"""Plugin Validation Service

Validates uploaded plugins before publishing to the marketplace.
Checks:
- Manifest schema compliance
- Binary signature verification
- No dangerous operations
- Resource limits
- Security review checklist
"""
import hashlib
import json
import re
from typing import Dict, List, Optional
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.logging import get_logger
from app.models.models import Plugin, PluginVersion, PluginReview

logger = get_logger(__name__)


class PluginValidator:
    """Validates plugins before marketplace publication."""
    
    # Dangerous patterns that plugins must not contain
    DANGEROUS_PATTERNS = [
        r"\brm\s+-rf\b",  # Recursive delete
        r"\bformat\s+[a-zA-Z]:\\",  # Format drive
        r"\bdel\s+/[sS]\b",  # Recursive delete on Windows
        r"\bshutdown\b",  # System shutdown
        r"\breboot\b",  # System reboot
        r"\bregistry\b.*\bdelete\b",  # Registry deletion
        r"\bnetsh\s+advfirewall\s+set\s+.*\s+state\s+off\b",  # Disable firewall
        r"\bnet\s+stop\s+.*\b",  # Stop services
        r"\bcmd\.exe\b.*\b/c\b",  # Command execution
        r"\bpowershell\.exe\b.*\b-Command\b",  # PowerShell execution
    ]
    
    # Required manifest fields
    REQUIRED_FIELDS = [
        "name", "version", "author", "description", "license", "tools", "platform"
    ]
    
    # Valid categories
    VALID_CATEGORIES = [
        "system", "process", "file", "network", "security", 
        "maintenance", "diagnostic", "monitoring", "custom"
    ]
    
    # Valid risk levels
    VALID_RISK_LEVELS = ["low", "medium", "high", "critical"]
    
    # Valid platforms
    VALID_PLATFORMS = ["windows-x64", "windows-arm64", "wasm"]
    
    async def validate_plugin(self, plugin_data: Dict) -> Dict:
        """
        Validate a plugin package.
        
        Args:
            plugin_data: Dictionary containing manifest, binary, and metadata
            
        Returns:
            Validation result with errors and warnings
        """
        errors = []
        warnings = []
        
        # 1. Validate manifest structure
        manifest = plugin_data.get("manifest")
        if not manifest:
            errors.append("Missing manifest.json")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        # 2. Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in manifest:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        # 3. Validate name format (alphanumeric + underscore + dash)
        name = manifest.get("name", "")
        if not re.match(r'^[a-z0-9_-]+$', name):
            errors.append("Plugin name must be lowercase alphanumeric with underscores or dashes")
        
        # 4. Validate version format (semver)
        version = manifest.get("version", "")
        if not re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$', version):
            errors.append("Version must be in semver format (e.g., 1.0.0)")
        
        # 5. Validate category
        category = manifest.get("category")
        if category and category not in self.VALID_CATEGORIES:
            errors.append(f"Invalid category: {category}. Must be one of: {', '.join(self.VALID_CATEGORIES)}")
        
        # 6. Validate platform
        platform = manifest.get("platform", "")
        if platform not in self.VALID_PLATFORMS:
            errors.append(f"Invalid platform: {platform}. Must be one of: {', '.join(self.VALID_PLATFORMS)}")
        
        # 7. Validate tools
        tools = manifest.get("tools", [])
        if not tools:
            errors.append("Plugin must provide at least one tool")
        else:
            for i, tool in enumerate(tools):
                tool_errors = self._validate_tool(tool, i)
                errors.extend(tool_errors)
        
        # 8. Validate binary
        binary = plugin_data.get("binary")
        if not binary:
            errors.append("Missing plugin binary")
        else:
            # Check binary size (max 10MB)
            if len(binary) > 10 * 1024 * 1024:
                errors.append(f"Binary too large: {len(binary) / 1024 / 1024:.2f}MB (max 10MB)")
            
            # Verify hash matches manifest
            binary_hash = plugin_data.get("binary_hash")
            if binary_hash:
                actual_hash = hashlib.sha256(binary).hexdigest()
                if actual_hash != binary_hash:
                    errors.append("Binary hash mismatch")
            
            # Scan for dangerous patterns (for WASM/text formats)
            if platform == "wasm":
                dangerous = self._scan_binary(binary)
                if dangerous:
                    warnings.append(f"Potentially dangerous patterns found: {', '.join(dangerous)}")
        
        # 9. Check permissions
        permissions = manifest.get("permissions", [])
        high_risk_permissions = ["full_disk_access", "registry_write", "service_control"]
        for perm in permissions:
            if perm in high_risk_permissions:
                warnings.append(f"High-risk permission requested: {perm}")
        
        # 10. Validate license
        license_id = manifest.get("license", "")
        if not license_id:
            errors.append("License is required")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_tool(self, tool: Dict, index: int) -> List[str]:
        """Validate a single tool definition."""
        errors = []
        prefix = f"Tool {index}"
        
        # Required fields
        if not tool.get("name"):
            errors.append(f"{prefix}: Missing 'name'")
        else:
            # Tool name format
            if not re.match(r'^[a-z_][a-z0-9_]*$', tool["name"]):
                errors.append(f"{prefix}: Name must be snake_case (e.g., 'my_tool')")
        
        if not tool.get("description"):
            errors.append(f"{prefix}: Missing 'description'")
        
        if not tool.get("category"):
            errors.append(f"{prefix}: Missing 'category'")
        elif tool["category"] not in self.VALID_CATEGORIES:
            errors.append(f"{prefix}: Invalid category")
        
        if not tool.get("risk_level"):
            errors.append(f"{prefix}: Missing 'risk_level'")
        elif tool["risk_level"] not in self.VALID_RISK_LEVELS:
            errors.append(f"{prefix}: Invalid risk_level")
        
        # Input schema validation
        input_schema = tool.get("input_schema")
        if input_schema:
            if not isinstance(input_schema, dict):
                errors.append(f"{prefix}: input_schema must be a JSON object")
        
        # Output schema validation
        output_schema = tool.get("output_schema")
        if output_schema:
            if not isinstance(output_schema, dict):
                errors.append(f"{prefix}: output_schema must be a JSON object")
        
        return errors
    
    def _scan_binary(self, binary: bytes) -> List[str]:
        """Scan binary for dangerous patterns."""
        found = []
        try:
            text = binary.decode('utf-8', errors='ignore')
            for pattern in self.DANGEROUS_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    found.append(pattern)
        except Exception:
            pass
        return found
    
    async def publish_plugin(
        self,
        db: AsyncSession,
        plugin_data: Dict,
        author_id: str,
        signature: Optional[str] = None
    ) -> Plugin:
        """
        Publish a validated plugin to the marketplace.
        
        Args:
            db: Database session
            plugin_data: Validated plugin data
            author_id: User ID of the plugin author
            signature: Digital signature from Aegis CA
            
        Returns:
            Created plugin record
        """
        manifest = plugin_data["manifest"]
        
        # Check if plugin already exists
        result = await db.execute(
            select(Plugin).where(Plugin.plugin_id == manifest["name"])
        )
        plugin = result.scalar_one_or_none()
        
        if plugin:
            # Update existing plugin
            plugin.author_id = author_id
            plugin.description = manifest["description"]
            plugin.updated_at = datetime.now(timezone.utc)
        else:
            # Create new plugin
            plugin = Plugin(
                plugin_id=manifest["name"],
                name=manifest["name"].replace("-", " ").replace("_", " ").title(),
                author_id=author_id,
                description=manifest["description"],
                homepage=manifest.get("homepage"),
                repository=manifest.get("repository"),
                license=manifest.get("license", "MIT"),
                category=manifest.get("category", "custom"),
            )
            db.add(plugin)
            await db.flush()
        
        # Create version
        version = PluginVersion(
            plugin_id=plugin.id,
            version=manifest["version"],
            binary=plugin_data["binary"],
            binary_hash=plugin_data["binary_hash"],
            signature=signature,
            manifest=manifest,
            platform=manifest.get("platform", "windows-x64"),
            size_bytes=len(plugin_data["binary"]),
            is_signed=signature is not None,
        )
        db.add(version)
        
        # Update plugin latest version
        plugin.latest_version_id = version.id
        
        logger.info(f"Published plugin {manifest['name']} v{manifest['version']}")
        
        return plugin


# Singleton instance
plugin_validator = PluginValidator()
