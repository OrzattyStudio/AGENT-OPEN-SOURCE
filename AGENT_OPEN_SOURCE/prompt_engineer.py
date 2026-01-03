"""
SYNTHESIS - PromptEngineerAgent (Open Source Version)
LLM Prompt Optimization
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class PromptEngineerAgent(BaseAgent):
    """
    PromptEngineerAgent - Optimizes prompts (simulated).
    """

    def __init__(self):
        super().__init__(
            name="PromptEngineerAgent",
            capabilities=[
                AgentCapability.REASONING, AgentCapability.PLANNING
            ]
        )
        self.register_tool("optimize_prompt", self.optimize_prompt, "Improves prompt clarity")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute prompt tasks.
        Input: { "action": "optimize", "prompt": "..." }
        """
        action = input_data.get("action")
        
        if action == "optimize":
            prompt = input_data.get("prompt", "")
            better = await self.execute_tool("optimize_prompt", prompt=prompt)
            return self.create_success_result(
                data={"optimized": better},
                message="Prompt optimized"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def optimize_prompt(self, prompt: str) -> str:
        """Optimize Prompt"""
        self.log_thought(f"Refining prompt: {prompt}")
        return f"Please act as an expert. {prompt}. Think step-by-step."
