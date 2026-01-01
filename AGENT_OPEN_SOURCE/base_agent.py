"""
SYNTHESIS - Base Agent Framework (Open Source)
Core architecture for autonomous AI agents

This is the foundation that enables 49+ agents to work together autonomously.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class AgentCapability(Enum):
    """Capabilities that agents can have"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"
    TESTING = "testing"
    ARCHITECTURE = "architecture"
    SECURITY_ANALYSIS = "security_analysis"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    DOCUMENTATION = "documentation"
    DATABASE_DESIGN = "database_design"
    API_DESIGN = "api_design"
    FRONTEND_DEVELOPMENT = "frontend_development"
    BACKEND_DEVELOPMENT = "backend_development"
    DEVOPS = "devops"
    PLANNING = "planning"
    REASONING = "reasoning"


@dataclass
class AgentResult:
    """Result from agent execution"""
    success: bool
    data: Dict[str, Any]
    message: str
    error: Optional[str] = None


class BaseAgent(ABC):
    """
    Base class for all SYNTHESIS agents.

    This framework enables:
    - Autonomous execution
    - Memory management
    - Error handling
    - Inter-agent communication
    - Security validation
    """

    def __init__(
        self,
        name: str,
        capabilities: List[AgentCapability],
        max_memory_mb: int = 50
    ):
        self.name = name
        self.capabilities = capabilities
        self.max_memory_mb = max_memory_mb
        self._memory_usage = 0.0

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute the agent's main task.

        Args:
            input_data: Input data for the task

        Returns:
            AgentResult with success status and data
        """
        pass

    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.capabilities

    def sanitize_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize output for security"""
        # Remove sensitive patterns
        sensitive_patterns = [
            r'password', r'secret', r'key', r'token', r'api_key', r'private'
        ]

        def sanitize_value(value):
            if isinstance(value, str):
                for pattern in sensitive_patterns:
                    import re
                    value = re.sub(rf'\b{pattern}\b.*', '[REDACTED]', value, flags=re.IGNORECASE)
                return value
            elif isinstance(value, dict):
                return {k: sanitize_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [sanitize_value(item) for item in value]
            return value

        return sanitize_value(data.copy())

    def create_success_result(self, data: Dict[str, Any], message: str) -> AgentResult:
        """Create a successful result"""
        return AgentResult(
            success=True,
            data=self.sanitize_output(data),
            message=message
        )

    def create_error_result(self, message: str, error: str) -> AgentResult:
        """Create an error result"""
        return AgentResult(
            success=False,
            data={},
            message=message,
            error=error
        )

    async def safe_execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute with error handling and memory management"""
        try:
            # Check memory limits
            if not self.check_memory_limits():
                return self.create_error_result(
                    "Memory limit exceeded",
                    "Agent memory usage too high"
                )

            result = await self.execute(input_data)

            # Cleanup memory
            self.cleanup_memory()

            return result

        except Exception as e:
            return self.create_error_result(
                f"{self.name} execution failed",
                str(e)
            )

    def check_memory_limits(self) -> bool:
        """Check if within memory limits"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            self._memory_usage = memory_mb
            return memory_mb < self.max_memory_mb
        except ImportError:
            return True  # Skip check if psutil not available

    def cleanup_memory(self) -> None:
        """Clean up memory usage"""
        import gc
        gc.collect()
        self._memory_usage = 0.0