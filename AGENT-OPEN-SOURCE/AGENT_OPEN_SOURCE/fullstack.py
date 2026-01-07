"""
SYNTHESIS - FullstackAgent (Open Source Version)
Full-stack development and integration
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class FullstackAgent(BaseAgent):
    """
    FullstackAgent - Coordinates basic frontend + backend scaffolding.
    """

    def __init__(self):
        super().__init__(
            name="FullstackAgent",
            capabilities=[
                AgentCapability.BACKEND_DEVELOPMENT, AgentCapability.FRONTEND_DEVELOPMENT
            ]
        )
        self.register_tool("scaffold_project", self.scaffold_project, "Generates folder structure for fullstack app")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute fullstack tasks.
        Input: { "action": "structure", "stack": "mern|pern" }
        """
        action = input_data.get("action")
        
        if action == "structure":
            stack = input_data.get("stack", "pern")
            structure = await self.execute_tool("scaffold_project", stack=stack)
            return self.create_success_result(
                data={"structure": structure},
                message=f"Generated structure for {stack}"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def scaffold_project(self, stack: str) -> Dict[str, Any]:
        """Generate project structure"""
        self.log_thought(f"Planning {stack} project structure")
        
        return {
            "root": {
                "client": {"description": "Frontend App (React)"},
                "server": {"description": "Backend API (Node/Python)"},
                "docker-compose.yml": "Container orchestration",
                "README.md": "Documentation"
            }
        }
