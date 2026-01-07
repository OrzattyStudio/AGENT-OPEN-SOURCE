"""
SYNTHESIS - SecurityAgent (Open Source Version)
Security analysis and vulnerability assessment specialist
"""

from typing import Dict, Any, List
import re
from .base_agent import BaseAgent, AgentCapability, AgentResult

class SecurityAgent(BaseAgent):
    """
    SecurityAgent - Performs static analysis to find common security issues (secrets, unsafe patterns).
    """

    def __init__(self):
        super().__init__(
            name="SecurityAgent",
            capabilities=[
                AgentCapability.SECURITY_ANALYSIS, AgentCapability.CODE_REVIEW
            ]
        )
        self.register_tool("scan_secrets", self.scan_secrets, "Scans code for hardcoded secrets")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute security scan.
        Input format:
        {
            "action": "scan_code",
            "content": "code_string_to_scan"
        }
        """
        action = input_data.get("action")
        
        if action == "scan_code":
            content = input_data.get("content", "")
            findings = await self.execute_tool("scan_secrets", content=content)
            
            if findings:
                return self.create_success_result(
                    data={"findings": findings, "status": "vulnerable"},
                    message=f"Found {len(findings)} potential security issues."
                )
            else:
                return self.create_success_result(
                    data={"findings": [], "status": "clean"},
                    message="No obvious security issues found."
                )
        else:
             return self.create_error_result("Unknown action", f"Action '{action}' is not supported")

    def scan_secrets(self, content: str) -> List[Dict[str, Any]]:
        """Scan content for potential secrets using Regex"""
        self.log_thought("Scanning content for hardcoded secrets...")
        
        patterns = {
            "AWS Access Key": r"AKIA[0-9A-Z]{16}",
            "Generic API Key": r"api_key\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]",
            "Hardcoded Password": r"password\s*=\s*['\"][^'\"]{3,}['\"]",
            "Private Key": r"-----BEGIN PRIVATE KEY-----"
        }
        
        findings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            for issue_type, pattern in patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    # Redact the secret in the output
                    redacted_line = re.sub(pattern, "[REDACTED]", line)
                    findings.append({
                        "line": i + 1,
                        "type": issue_type,
                        "content": redacted_line.strip()
                    })
                    
        return findings
