"""
SYNTHESIS - ConfigAgent (Open Source Version)
Configuration management and environment handling
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult
import json

class ConfigAgent(BaseAgent):
    """
    ConfigAgent - Manages configuration files (JSON, YAML, .env).
    """

    def __init__(self):
        super().__init__(
            name="ConfigAgent",
            capabilities=[
                AgentCapability.DEVOPS, AgentCapability.CODE_GENERATION
            ]
        )
        self.register_tool("generate_config", self.generate_config, "Generates default config files")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute config tasks.
        Input: { "action": "generate", "format": "json|env", "settings": {...} }
        """
        action = input_data.get("action")
        
        if action == "generate":
            fmt = input_data.get("format", "json")
            settings = input_data.get("settings", {})
            config = await self.execute_tool("generate_config", fmt=fmt, settings=settings)
            
            return self.create_success_result(
                data={"config": config, "format": fmt},
                message=f"Generated {fmt} configuration"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def generate_config(self, fmt: str, settings: Dict[str, Any]) -> str:
        """Generate configuration string"""
        self.log_thought(f"Generating {fmt} config with {len(settings)} settings")
        
        if fmt == "json":
            return json.dumps(settings, indent=2)
        elif fmt == "env":
            return "\n".join([f"{k.upper()}={v}" for k, v in settings.items()])
        else:
            return "# Format not supported"
