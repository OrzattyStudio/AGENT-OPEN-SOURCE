"""
SYNTHESIS - DocumentationAgent (Open Source Version)
Documentation generation and maintenance
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class DocumentationAgent(BaseAgent):
    """
    DocumentationAgent - Generates Docstrings/README stubs.
    """

    def __init__(self):
        super().__init__(
            name="DocumentationAgent",
            capabilities=[
                AgentCapability.DOCUMENTATION, AgentCapability.CODE_GENERATION
            ]
        )
        self.register_tool("generate_docstring", self.generate_docstring, "Generates Python docstring")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute documentation tasks.
        Input: { "action": "docstring", "func_name": "my_func", "params": ["a", "b"] }
        """
        action = input_data.get("action")
        
        if action == "docstring":
            func = input_data.get("func_name", "func")
            params = input_data.get("params", [])
            doc = await self.execute_tool("generate_docstring", func=func, params=params)
            return self.create_success_result(
                data={"docstring": doc},
                message=f"Generated docstring for {func}"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def generate_docstring(self, func: str, params: list) -> str:
        """Generate Docstring"""
        self.log_thought(f"Generating docstring for {func}")
        param_str = "\n".join([f"    {p}: Description for {p}" for p in params])
        return f'"""\nDescription for {func}.\n\nArgs:\n{param_str}\n\nReturns:\n    None\n"""'
