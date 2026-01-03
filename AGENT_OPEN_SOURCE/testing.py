"""
SYNTHESIS - TestingAgent (Open Source Version)
Automated testing and test generation specialist
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class TestingAgent(BaseAgent):
    """
    TestingAgent - Generates Pytest or generic test boilerplates.
    """

    def __init__(self):
        super().__init__(
            name="TestingAgent",
            capabilities=[
                AgentCapability.TESTING, AgentCapability.CODE_GENERATION
            ]
        )
        self.register_tool("generate_test_file", self.generate_test_file, "Generates unit test boilerplate")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute testing tasks.
        Input: { "action": "generate_tests", "target_module": "...", "framework": "pytest" }
        """
        action = input_data.get("action")
        
        if action == "generate_tests":
            target = input_data.get("target_module", "app")
            framework = input_data.get("framework", "pytest")
            code = await self.execute_tool("generate_test_file", target=target, framework=framework)
            return self.create_success_result(
                data={"code": code, "filename": f"test_{target}.py"},
                message=f"Generated {framework} tests for {target}"
            )
        else:
             return self.create_error_result("Unknown action", f"Action '{action}' not supported")

    def generate_test_file(self, target: str, framework: str) -> str:
        """Generate test code boilerplate"""
        self.log_thought(f"Writing {framework} tests for module: {target}")
        
        if framework == "pytest":
            return f"""import pytest
from {target} import *

def test_initialization():
    assert True

def test_functionality():
    # TODO: Implement specific test cases for {target}
    assert 1 + 1 == 2

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4)
])
def test_parametrized(input, expected):
    pass
"""
        elif framework == "unittest":
             return f"""import unittest
from {target} import *

class Test{target.capitalize()}(unittest.TestCase):
    def setUp(self):
        pass

    def test_basic(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
"""
        else:
            return "# Framework not supported"
