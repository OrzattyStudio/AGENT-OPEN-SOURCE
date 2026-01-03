
import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
    artifacts: List[str] = field(default_factory=list)


class BaseAgent(ABC):
    """
    Base class for all SYNTHESIS agents (Open Source Version).
    
    This framework provides a structure for creating deterministic, rule-based agents
    that can perform useful development tasks suitable for local execution.
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
        self.logger = logging.getLogger(self.name)
        self.tools: Dict[str, Callable] = {}
        
        # Register default tools logic if any
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default tools available to all agents"""
        pass

    def register_tool(self, name: str, func: Callable, description: str):
        """Register a new tool capability for this agent"""
        self.tools[name] = func
        self.logger.info(f"Tool registered: {name} - {description}")

    def log_thought(self, thought: str):
        """Simulate agent thinking/reasoning process"""
        self.logger.info(f"THOUGHT: {thought}")
        print(f"[{self.name}] Thinking: {thought}")

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute the agent's main task.
        Must be implemented by specific agents.
        """
        pass

    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a registered tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found in {self.name}")
        
        self.log_thought(f"Executing tool: {tool_name} with params: {list(kwargs.keys())}")
        try:
            # If tool is async, await it
            if asyncio.iscoroutinefunction(self.tools[tool_name]):
                return await self.tools[tool_name](**kwargs)
            return self.tools[tool_name](**kwargs)
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            raise e

    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.capabilities

    def create_success_result(self, data: Dict[str, Any], message: str, artifacts: List[str] = None) -> AgentResult:
        """Create a successful result"""
        return AgentResult(
            success=True,
            data=data,
            message=message,
            artifacts=artifacts or []
        )

    def create_error_result(self, message: str, error: str) -> AgentResult:
        """Create an error result"""
        self.logger.error(f"Error: {message} - {error}")
        return AgentResult(
            success=False,
            data={},
            message=message,
            error=error
        )

    async def safe_execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute with error handling"""
        try:
            self.log_thought(f"Starting execution with input keys: {list(input_data.keys())}")
            result = await self.execute(input_data)
            self.log_thought("Execution completed successfully")
            return result
        except Exception as e:
            return self.create_error_result(
                f"{self.name} execution failed",
                str(e)
            )