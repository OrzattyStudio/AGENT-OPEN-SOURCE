"""
SYNTHESIS - SEOAgent (Open Source Version)
Search Engine Optimization specialist
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class SEOAgent(BaseAgent):
    """
    SEOAgent - Generates meta tags and robots.txt.
    """

    def __init__(self):
        super().__init__(
            name="SEOAgent",
            capabilities=[
                AgentCapability.CODE_GENERATION, AgentCapability.FRONTEND_DEVELOPMENT
            ]
        )
        self.register_tool("generate_meta", self.generate_meta, "Generates HTML meta tags")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute SEO tasks.
        Input: { "action": "meta", "title": "...", "desc": "..." }
        """
        action = input_data.get("action")
        
        if action == "meta":
            title = input_data.get("title", "Title")
            desc = input_data.get("desc", "Description")
            tags = await self.execute_tool("generate_meta", title=title, desc=desc)
            return self.create_success_result(
                data={"tags": tags},
                message="Generated SEO meta tags"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def generate_meta(self, title: str, desc: str) -> str:
        """Generate meta tags"""
        self.log_thought("Generating SEO meta tags...")
        return f"""<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow">"""
