"""
SYNTHESIS - EmbeddedAgent (Open Source Version)
Embedded systems and IoT development
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class EmbeddedAgent(BaseAgent):
    """
    EmbeddedAgent - Generates Arduino/C++ sketches for IoT.
    """

    def __init__(self):
        super().__init__(
            name="EmbeddedAgent",
            capabilities=[
                AgentCapability.CODE_GENERATION, AgentCapability.HARDWARE_INTERFACE
            ]
        )
        self.register_tool("generate_sketch", self.generate_sketch, "Generates Arduino sketches")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute embedded tasks.
        Input: { "action": "sketch", "module": "led_blink" }
        """
        action = input_data.get("action")
        
        if action == "sketch":
            module = input_data.get("module", "led_blink")
            code = await self.execute_tool("generate_sketch", module=module)
            return self.create_success_result(
                data={"code": code},
                message=f"Generated sketch for {module}"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def generate_sketch(self, module: str) -> str:
        """Generate Arduino code"""
        self.log_thought(f"Generating Arduino sketch for {module}")
        
        if module == "led_blink":
            return """void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(1000);
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);
}"""
        return "// Module not supported"
