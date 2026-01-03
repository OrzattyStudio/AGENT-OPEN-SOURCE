"""
SYNTHESIS - QAAgent (Open Source Version)
Quality Assurance and test automation
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentCapability, AgentResult

class QAAgent(BaseAgent):
    """
    QAAgent - Generates test plans and manual test checklists.
    """

    def __init__(self):
        super().__init__(
            name="QAAgent",
            capabilities=[
                AgentCapability.TESTING, AgentCapability.PLANNING
            ]
        )
        self.register_tool("generate_test_plan", self.generate_test_plan, "Generates QA Test Plan")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute QA tasks.
        Input: { "action": "plan", "feature": "Login" }
        """
        action = input_data.get("action")
        
        if action == "plan":
            feature = input_data.get("feature", "General")
            plan = await self.execute_tool("generate_test_plan", feature=feature)
            return self.create_success_result(
                data={"plan": plan},
                message=f"Generated test plan for {feature}"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def generate_test_plan(self, feature: str) -> List[str]:
        """Generate simple test cases"""
        self.log_thought(f"Creating test plan for {feature}")
        return [
            f"Verify {feature} loads correctly",
            f"Test {feature} with valid input",
            f"Test {feature} with invalid input",
            f"Check error messages for {feature}",
            f"Verify {feature} performance under load"
        ]
