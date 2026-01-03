"""
SYNTHESIS - ReviewerAgent (Open Source Version)
Code review and quality assessment
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class ReviewerAgent(BaseAgent):
    """
    ReviewerAgent - Auto-reviews code against style guides.
    """

    def __init__(self):
        super().__init__(
            name="ReviewerAgent",
            capabilities=[
                AgentCapability.CODE_REVIEW, AgentCapability.SECURITY_ANALYSIS
            ]
        )
        self.register_tool("review_code", self.review_code, "Checks for style violations (PEP8-ish)")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute review tasks.
        Input: { "action": "review", "code": "..." }
        """
        action = input_data.get("action")
        
        if action == "review":
            feedback = await self.execute_tool("review_code", code=input_data.get("code", ""))
            return self.create_success_result(
                data={"feedback": feedback},
                message="Code review complete"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def review_code(self, code: str) -> list[str]:
        """Review code style"""
        self.log_thought("Reviewing code against style guide...")
        issues = []
        if len(code) > 1000:
            issues.append("File likely too long, consider splitting.")
        if "print(" in code:
            issues.append("Remove print statements before production.")
        return issues if issues else ["Code looks clean!"]
