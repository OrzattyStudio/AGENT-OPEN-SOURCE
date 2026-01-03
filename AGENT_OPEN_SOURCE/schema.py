"""
SYNTHESIS - SchemaAgent (Open Source Version)
Data schema definition and validation
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult
import json

class SchemaAgent(BaseAgent):
    """
    SchemaAgent - Generates JSON Schemas.
    """

    def __init__(self):
        super().__init__(
            name="SchemaAgent",
            capabilities=[
                AgentCapability.DATABASE_DESIGN, AgentCapability.CODE_GENERATION
            ]
        )
        self.register_tool("generate_json_schema", self.generate_json_schema, "Generates JSON Schema from dict")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute schema tasks.
        Input: { "action": "json_schema", "example": {...} }
        """
        action = input_data.get("action")
        
        if action == "json_schema":
            example = input_data.get("example", {})
            schema = await self.execute_tool("generate_json_schema", example=example)
            return self.create_success_result(
                data={"schema": schema},
                message="Generated JSON Schema"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def generate_json_schema(self, example: Dict[str, Any]) -> str:
        """Generate JSON Schema"""
        self.log_thought("Inferring JSON Schema from example...")
        schema = {"type": "object", "properties": {}}
        for k, v in example.items():
            t = "string"
            if isinstance(v, bool): t = "boolean"
            elif isinstance(v, int): t = "integer"
            elif isinstance(v, float): t = "number"
            elif isinstance(v, list): t = "array"
            schema["properties"][k] = {"type": t}
        return json.dumps(schema, indent=2)
