"""
SYNTHESIS - ArchitectAgent (Open Source Version)
System architecture and high-level design
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class ArchitectAgent(BaseAgent):
    """
    ArchitectAgent - Generates high-level system diagrams (Mermaid).
    """

    def __init__(self):
        super().__init__(
            name="ArchitectAgent",
            capabilities=[
                AgentCapability.ARCHITECTURE, AgentCapability.PLANNING
            ]
        )
        self.register_tool("generate_diagram", self.generate_diagram, "Generates Mermaid.js architecture diagram")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute architecture tasks.
        Input: { "action": "diagram", "type": "flowchart" }
        """
        action = input_data.get("action")
        
        if action == "diagram":
            dtype = input_data.get("type", "flowchart")
            diagram = await self.execute_tool("generate_diagram", dtype=dtype)
            return self.create_success_result(
                data={"mermaid": diagram},
                message=f"Generated {dtype} diagram"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def generate_diagram(self, dtype: str) -> str:
        """Generate Mermaid Diagram"""
        self.log_thought(f"Designing {dtype} architecture...")
        return """graph TD
    Client --> API
    API --> Database
    API --> Cache"""