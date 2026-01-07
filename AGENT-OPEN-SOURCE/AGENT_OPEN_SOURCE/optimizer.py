"""
SYNTHESIS - OptimizerAgent (Open Source Version)
Code and Database query optimization
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class OptimizerAgent(BaseAgent):
    """
    OptimizerAgent - Analyzes SQL/Code for efficiency.
    """

    def __init__(self):
        super().__init__(
            name="OptimizerAgent",
            capabilities=[
                AgentCapability.PERFORMANCE_OPTIMIZATION, AgentCapability.DATABASE_DESIGN
            ]
        )
        self.register_tool("optimize_sql", self.optimize_sql, "Suggests SQL indexing")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute optimization tasks.
        Input: { "action": "optimize_sql", "query": "SELECT..." }
        """
        action = input_data.get("action")
        
        if action == "optimize_sql":
            query = input_data.get("query", "")
            advice = await self.execute_tool("optimize_sql", query=query)
            return self.create_success_result(
                data={"advice": advice},
                message="SQL optimization advice generated"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def optimize_sql(self, query: str) -> str:
        """Analyze SQL"""
        self.log_thought("Analyzing SQL query for missing indexes...")
        if "WHERE" in query:
             return "Ensure columns in WHERE clause are indexed."
        return "Query looks simple. Consider limit if table is large."
