"""Validate agent YAML against schema requirements."""

import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any


class AgentYAMLValidator:
    """Validator for agent YAML schema based on AGENT_YAML_SCHEMA.md"""
    
    VALID_KINDS = ["Prompt", "Agent"]
    VALID_CONNECTION_KINDS = ["remote", "key", "reference", "anonymous"]
    VALID_TOOL_KINDS = [
        "function", "web_search", "file_search", "code_interpreter",
        "mcp", "openapi", "custom"
    ]
    
    def __init__(self, yaml_file: str):
        self.yaml_file = Path(yaml_file)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.agent_data: Dict[str, Any] = {}
    
    def validate(self) -> bool:
        """Run all validations. Returns True if valid."""
        
        if not self.yaml_file.exists():
            self.errors.append(f"File not found: {self.yaml_file}")
            return False
        
        # Load YAML
        try:
            with open(self.yaml_file) as f:
                self.agent_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML syntax: {e}")
            return False
        
        # Run validations
        self._validate_required_fields()
        self._validate_kind()
        self._validate_model()
        self._validate_tools()
        self._check_powerfx_expressions()
        
        return len(self.errors) == 0
    
    def _validate_required_fields(self):
        """Check required top-level fields."""
        required = ["kind", "name"]
        for field in required:
            if field not in self.agent_data:
                self.errors.append(f"Missing required field: '{field}'")
    
    def _validate_kind(self):
        """Validate 'kind' field."""
        kind = self.agent_data.get("kind")
        if kind and kind not in self.VALID_KINDS:
            self.errors.append(
                f"Invalid 'kind': '{kind}' (must be one of {self.VALID_KINDS})"
            )
    
    def _validate_model(self):
        """Validate model configuration."""
        model = self.agent_data.get("model")
        if not model:
            self.warnings.append("No 'model' section defined")
            return
        
        # Check model.id
        if "id" not in model:
            self.errors.append("Missing required field: 'model.id'")
        
        # Check connection if present
        connection = model.get("connection")
        if connection:
            conn_kind = connection.get("kind")
            if not conn_kind:
                self.errors.append("Missing required field: 'model.connection.kind'")
            elif conn_kind not in self.VALID_CONNECTION_KINDS:
                self.errors.append(
                    f"Invalid connection kind: '{conn_kind}' "
                    f"(must be one of {self.VALID_CONNECTION_KINDS})"
                )
            
            # Validate connection-specific required fields
            if conn_kind == "remote" and "endpoint" not in connection:
                self.errors.append("'remote' connection requires 'endpoint'")
            elif conn_kind == "key":
                if "apiKey" not in connection and "key" not in connection:
                    self.errors.append("'key' connection requires 'apiKey' or 'key'")
            elif conn_kind == "reference" and "name" not in connection:
                self.errors.append("'reference' connection requires 'name'")
            elif conn_kind == "anonymous" and "endpoint" not in connection:
                self.errors.append("'anonymous' connection requires 'endpoint'")
    
    def _validate_tools(self):
        """Validate tools configuration."""
        tools = self.agent_data.get("tools", [])
        
        for i, tool in enumerate(tools):
            tool_kind = tool.get("kind")
            
            if not tool_kind:
                self.errors.append(f"Tool #{i+1}: Missing 'kind' field")
                continue
            
            if tool_kind not in self.VALID_TOOL_KINDS:
                self.errors.append(
                    f"Tool #{i+1}: Invalid kind '{tool_kind}' "
                    f"(must be one of {self.VALID_TOOL_KINDS})"
                )
            
            # Tool-specific validations
            if tool_kind == "function":
                if "name" not in tool:
                    self.errors.append(f"Tool #{i+1}: 'function' tool requires 'name'")
                if "description" not in tool:
                    self.errors.append(f"Tool #{i+1}: 'function' tool requires 'description'")
            
            elif tool_kind == "mcp":
                if "name" not in tool:
                    self.errors.append(f"Tool #{i+1}: 'mcp' tool requires 'name'")
                if "url" not in tool:
                    self.errors.append(f"Tool #{i+1}: 'mcp' tool requires 'url'")
            
            elif tool_kind == "openapi":
                if "name" not in tool:
                    self.errors.append(f"Tool #{i+1}: 'openapi' tool requires 'name'")
                if "specification" not in tool:
                    self.errors.append(f"Tool #{i+1}: 'openapi' tool requires 'specification'")
            
            elif tool_kind == "custom":
                if "name" not in tool:
                    self.errors.append(f"Tool #{i+1}: 'custom' tool requires 'name'")
    
    def _check_powerfx_expressions(self):
        """Find and report PowerFx expressions."""
        expressions = []
        
        def find_expressions(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    find_expressions(v, f"{path}.{k}" if path else k)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    find_expressions(item, f"{path}[{i}]")
            elif isinstance(obj, str) and obj.startswith("="):
                expressions.append((path, obj))
        
        find_expressions(self.agent_data)
        
        if expressions:
            print("\n📝 PowerFx expressions found:")
            for path, expr in expressions:
                print(f"   {path}: {expr}")
                # Extract environment variables
                if expr.startswith("=Env."):
                    var_name = expr.split("=Env.")[1].split(")")[0].split(",")[0]
                    print(f"      → Requires env var: {var_name}")
    
    def print_results(self):
        """Print validation results."""
        print(f"\n{'='*60}")
        print(f"Validating: {self.yaml_file.name}")
        print(f"{'='*60}")
        
        if self.errors:
            print(f"\n❌ Validation FAILED with {len(self.errors)} error(s):")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} warning(s):")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if not self.errors:
            print(f"\n✅ Validation PASSED!")
            print(f"   Agent name: {self.agent_data.get('name')}")
            print(f"   Agent kind: {self.agent_data.get('kind')}")
            if 'description' in self.agent_data:
                print(f"   Description: {self.agent_data.get('description')}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_yaml.py <path-to-agent.yaml>")
        print("Example: python validate_yaml.py agents/mslearnagent.yaml")
        sys.exit(1)
    
    validator = AgentYAMLValidator(sys.argv[1])
    is_valid = validator.validate()
    validator.print_results()
    
    sys.exit(0 if is_valid else 1)
