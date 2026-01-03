"""
SYNTHESIS - DevOpsAgent (Open Source Version)
DevOps and infrastructure automation specialist
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentCapability, AgentResult

class DevOpsAgent(BaseAgent):
    """
    DevOpsAgent - Generates Dockerfiles and CI/CD configurations.
    """

    def __init__(self):
        super().__init__(
            name="DevOpsAgent",
            capabilities=[
                AgentCapability.DEVOPS, AgentCapability.ARCHITECTURE
            ]
        )
        self.register_tool("generate_dockerfile", self.generate_dockerfile, "Generates Dockerfile for standard stacks")
        self.register_tool("generate_ci_config", self.generate_ci_config, "Generates GitHub Actions workflow")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute devops tasks.
        Input format:
        {
            "action": "generate_dockerfile" | "generate_ci",
            "stack": "python" | "node",
            ...
        }
        """
        action = input_data.get("action")
        
        if action == "generate_dockerfile":
            stack = input_data.get("stack", "python")
            code = await self.execute_tool("generate_dockerfile", stack=stack)
            return self.create_success_result(
                data={"code": code, "filename": "Dockerfile"},
                message=f"Generated Dockerfile for {stack}"
            )
            
        elif action == "generate_ci_config":
            platform = input_data.get("platform", "github")
            code = await self.execute_tool("generate_ci_config", platform=platform)
            return self.create_success_result(
                data={"code": code, "filename": "ci-workflow.yml"},
                message=f"Generated CI config for {platform}"
            )
        else:
             return self.create_error_result("Unknown action", f"Action '{action}' is not supported")

    def generate_dockerfile(self, stack: str) -> str:
        """Generate Dockerfile boilerplate"""
        self.log_thought(f"Generating Dockerfile for {stack}")
        
        if stack == "python":
            return """# Python Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
"""
        elif stack == "node":
            return """# Node.js Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000
CMD ["npm", "start"]
"""
        else:
             return "# Stack not supported for auto-generation yet"

    def generate_ci_config(self, platform: str) -> str:
        """Generate CI Config"""
        self.log_thought(f"Generating CI/CD config for {platform}")
        
        if platform == "github":
            return """name: CI Pipeline

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run Tests
      run: echo "Running tests..."
"""
        return "# Only GitHub Actions supported currently"
