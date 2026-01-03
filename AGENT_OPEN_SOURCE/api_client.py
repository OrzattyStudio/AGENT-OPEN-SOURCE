"""
SYNTHESIS - APIClientAgent (Open Source Version)
External API integration
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class APIClientAgent(BaseAgent):
    """
    APIClientAgent - Generates API client code.
    """

    def __init__(self):
        super().__init__(
            name="APIClientAgent",
            capabilities=[
                AgentCapability.CODE_GENERATION, AgentCapability.BACKEND_DEVELOPMENT
            ]
        )
        self.register_tool("generate_client", self.generate_client, "Generates Requests client")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute API client tasks.
        Input: { "action": "client", "base_url": "..." }
        """
        action = input_data.get("action")
        
        if action == "client":
            url = input_data.get("base_url", "http://api.com")
            code = await self.execute_tool("generate_client", url=url)
            return self.create_success_result(
                data={"code": code},
                message=f"Generated client for {url}"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def generate_client(self, url: str) -> str:
        """Generate API Client"""
        self.log_thought(f"Generating client for {url}")
        return f"""import requests

class Client:
    def __init__(self):
        self.base_url = "{url}"

    def get_data(self):
        return requests.get(f"{{self.base_url}}/data").json()
"""
