"""
SYNTHESIS - DebuggerAgent (Open Source Version)
Code debugging and error resolution
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class DebuggerAgent(BaseAgent):
    """
    DebuggerAgent - Analyzes error logs (simulated).
    """

    def __init__(self):
        super().__init__(
            name="DebuggerAgent",
            capabilities=[
                AgentCapability.DEBUGGING, AgentCapability.CODE_GENERATION
            ]
        )
        self.register_tool("analyze_log", self.analyze_log, "Analyzes error logs for common patterns")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute debugging tasks.
        Input: { "action": "analyze", "log": "Error..." }
        """
        action = input_data.get("action")
        
        if action == "analyze":
            log = input_data.get("log", "")
            hints = await self.execute_tool("analyze_log", log=log)
            return self.create_success_result(
                data={"hints": hints},
                message="Log analysis complete"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def analyze_log(self, log: str) -> str:
        """Analyze log content"""
        self.log_thought("Analyzing error log...")
        if "NullPointerException" in log or "NoneType" in log:
            return "Potential null reference. Check if object is initialized."
        if "Timeout" in log:
            return "Operation timed out. Check network or performance."
        return "Unknown error pattern. Recommend manual review."
