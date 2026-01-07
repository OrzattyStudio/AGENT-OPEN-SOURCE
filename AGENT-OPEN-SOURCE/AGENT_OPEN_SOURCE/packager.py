"""
SYNTHESIS - PackagerAgent (Open Source Version)
Package management and distribution
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class PackagerAgent(BaseAgent):
    """
    PackagerAgent - Generates setup.py / package.json.
    """

    def __init__(self):
        super().__init__(
            name="PackagerAgent",
            capabilities=[
                AgentCapability.DEVOPS, AgentCapability.CODE_GENERATION
            ]
        )
        self.register_tool("generate_package_config", self.generate_package_config, "Generates setup.py or package.json")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute packager tasks.
        Input: { "action": "config", "type": "python", "name": "mypkg" }
        """
        action = input_data.get("action")
        
        if action == "config":
            ptype = input_data.get("type", "python")
            name = input_data.get("name", "pkg")
            code = await self.execute_tool("generate_package_config", ptype=ptype, name=name)
            return self.create_success_result(
                data={"code": code},
                message=f"Generated package config for {name}"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def generate_package_config(self, ptype: str, name: str) -> str:
        """Generate package config"""
        self.log_thought(f"Packaging {name} for {ptype}")
        if ptype == "python":
            return f"""from setuptools import setup, find_packages

setup(
    name="{name}",
    version="0.1.0",
    packages=find_packages(),
)"""
        return "{}"
