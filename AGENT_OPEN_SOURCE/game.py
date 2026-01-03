"""
SYNTHESIS - GameAgent (Open Source Version)
Game development and logic specialist
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class GameAgent(BaseAgent):
    """
    GameAgent - Generates game logic scripts (Unity/C# or Godot/GDScript).
    """

    def __init__(self):
        super().__init__(
            name="GameAgent",
            capabilities=[
                AgentCapability.CODE_GENERATION, AgentCapability.LOGIC
            ]
        )
        self.register_tool("generate_script", self.generate_script, "Generates basic game scripts")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute game tasks.
        Input: { "action": "script", "engine": "unity", "type": "movement" }
        """
        action = input_data.get("action")
        
        if action == "script":
            engine = input_data.get("engine", "unity")
            script_type = input_data.get("type", "movement")
            code = await self.execute_tool("generate_script", engine=engine, script_type=script_type)
            return self.create_success_result(
                data={"code": code},
                message=f"Generated {script_type} script for {engine}"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def generate_script(self, engine: str, script_type: str) -> str:
        """Generate Game Script"""
        self.log_thought(f"Generating {script_type} script for {engine}")
        
        if engine == "unity" and script_type == "movement":
            return """using UnityEngine;

public class PlayerMovement : MonoBehaviour {
    public float speed = 5f;

    void Update() {
        float h = Input.GetAxis("Horizontal");
        float v = Input.GetAxis("Vertical");
        transform.Translate(new Vector3(h, 0, v) * speed * Time.deltaTime);
    }
}"""
        return "// Script not available"
