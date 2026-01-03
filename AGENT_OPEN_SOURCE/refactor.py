"""
SYNTHESIS - RefactorAgent (Open Source Version)
Code refactoring and modernization
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class RefactorAgent(BaseAgent):
    """
    RefactorAgent - Suggests code structure improvements.
    """

    def __init__(self):
        super().__init__(
            name="RefactorAgent",
            capabilities=[
                AgentCapability.CODE_GENERATION, AgentCapability.CODE_REVIEW
            ]
        )
        self.register_tool("suggest_refactor", self.suggest_refactor, "Suggests refactoring patterns")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute refactoring tasks.
        Input: { "action": "suggest", "code": "..." }
        """
        action = input_data.get("action")
        
        if action == "suggest":
            advice = await self.execute_tool("suggest_refactor", code=input_data.get("code", ""))
            return self.create_success_result(
                data={"advice": advice},
                message="Refactoring suggestions generated"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def suggest_refactor(self, code: str) -> list[str]:
        """Suggest refactors"""
        self.log_thought("Analyzing code structure...")
        suggestions = ["Extract complex logic into functions"]
        if "global" in code:
            suggestions.append("Avoid global variables, use dependency injection")
        return suggestions
