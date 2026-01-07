"""
SYNTHESIS - CloudAgent (Open Source Version)
Cloud infrastructure and deployment specialist
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class CloudAgent(BaseAgent):
    """
    CloudAgent - Generates Infrastructure as Code (Terraform/CloudFormation).
    """

    def __init__(self):
        super().__init__(
            name="CloudAgent",
            capabilities=[
                AgentCapability.DEVOPS, AgentCapability.ARCHITECTURE
            ]
        )
        self.register_tool("generate_terraform", self.generate_terraform, "Generates Terraform resources")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute cloud tasks.
        Input: { "action": "generate_iac", "provider": "aws", "resource": "s3" }
        """
        action = input_data.get("action")
        
        if action == "generate_iac":
            provider = input_data.get("provider", "aws")
            resource = input_data.get("resource", "s3")
            code = await self.execute_tool("generate_terraform", provider=provider, resource=resource)
            return self.create_success_result(
                data={"code": code, "type": "terraform"},
                message=f"Generated Terraform for {provider} {resource}"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def generate_terraform(self, provider: str, resource: str) -> str:
        """Generate Terraform snippets"""
        self.log_thought(f"Generating Terraform for {provider} {resource}")
        
        if provider == "aws" and resource == "s3":
            return """resource "aws_s3_bucket" "b" {
  bucket = "my-tf-test-bucket"
  acl    = "private"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}"""
        elif provider == "aws" and resource == "ec2":
            return """resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    Name = "HelloWorld"
  }
}"""
        return "# Resource not available in basic CloudAgent"
