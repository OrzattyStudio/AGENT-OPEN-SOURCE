"""
SYNTHESIS - LegacyAgent (Open Source Version)
Legacy system maintenance and migration
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class LegacyAgent(BaseAgent):
    """
    LegacyAgent - Identifies deprecated code patterns.
    """

    def __init__(self):
        super().__init__(
            name="LegacyAgent",
            capabilities=[
                AgentCapability.CODE_REVIEW, AgentCapability.REFACTORING
            ]
        )
        self.register_tool("check_deprecation", self.check_deprecation, "Checks for deprecated Python 2 patterns")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute legacy tasks.
        Input: { "action": "check", "code": "print 'hello'" }
        """
        action = input_data.get("action")
        
        if action == "check":
            code = input_data.get("code", "")
            issues = await self.execute_tool("check_deprecation", code=code)
            return self.create_success_result(
                data={"issues": issues},
                message="Legacy code check complete"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def check_deprecation(self, code: str) -> list:
        """Check legacy patterns"""
        self.log_thought("Scanning for legacy patterns...")
        issues = []
        if "print " in code and "print(" not in code:
            issues.append("Python 2 print statement detected")
        if "xrange" in code:
            issues.append("xrange is deprecated in Python 3")
        return issues
