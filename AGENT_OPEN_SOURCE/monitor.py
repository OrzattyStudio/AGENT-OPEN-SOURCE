"""
SYNTHESIS - MonitorAgent (Open Source Version)
System monitoring and performance tracking
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult
import time

class MonitorAgent(BaseAgent):
    """
    MonitorAgent - Checks system status (simulated/local).
    """

    def __init__(self):
        super().__init__(
            name="MonitorAgent",
            capabilities=[
                AgentCapability.DEVOPS, AgentCapability.PERFORMANCE_OPTIMIZATION
            ]
        )
        self.register_tool("check_status", self.check_status, "Checks service availability")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute monitoring tasks.
        Input: { "action": "check", "endpoint": "http://..." }
        """
        action = input_data.get("action")
        
        if action == "check":
            endpoint = input_data.get("endpoint", "localhost")
            status = await self.execute_tool("check_status", endpoint=endpoint)
            return self.create_success_result(
                data={"status": status},
                message=f"Checked status of {endpoint}"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def check_status(self, endpoint: str) -> Dict[str, Any]:
        """Simulate status check"""
        self.log_thought(f"Pinging {endpoint}...")
        # In a real tool this would use requests.get
        return {
            "endpoint": endpoint,
            "status": "UP",
            "latency_ms": 45,
            "timestamp": time.time()
        }
