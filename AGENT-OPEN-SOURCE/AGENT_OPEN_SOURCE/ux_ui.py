"""
SYNTHESIS - UXUIAgent (Open Source Version)
User Experience and Interface Design
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class UXUIAgent(BaseAgent):
    """
    UXUIAgent - Generates CSS color palettes and style guides.
    """

    def __init__(self):
        super().__init__(
            name="UXUIAgent",
            capabilities=[
                AgentCapability.FRONTEND_DEVELOPMENT, AgentCapability.CODE_GENERATION
            ]
        )
        self.register_tool("generate_palette", self.generate_palette, "Generates CSS color variables")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute UX/UI tasks.
        Input: { "action": "palette", "base": "blue" }
        """
        action = input_data.get("action")
        
        if action == "palette":
            base = input_data.get("base", "blue")
            css = await self.execute_tool("generate_palette", base=base)
            return self.create_success_result(
                data={"css": css},
                message=f"Generated {base} color palette"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def generate_palette(self, base: str) -> str:
        """Generate CSS Palette"""
        self.log_thought(f"Creating color palette based on {base}")
        return f""":root {{
  --primary: {base};
  --primary-light: light{base};
  --primary-dark: dark{base};
  --text: #333;
  --bg: #fff;
}}"""
