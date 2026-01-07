"""
SYNTHESIS Open Source Agent Framework - Enterprise Base Agent

This is the core building block for all SYNTHESIS agents.
Features:
- LLM provider integration (OpenAI, Anthropic, Google, Groq, Ollama)
- Structured output parsing (JSON mode)
- Memory system for context management
- Tool calling framework
- Retry logic with exponential backoff
- Metrics and observability

Usage:
    from base_agent import BaseAgent, AgentCapability, AgentResult
    
    class MyAgent(BaseAgent):
        def __init__(self):
            super().__init__(
                name="MyAgent",
                capabilities=[AgentCapability.CODE_GENERATION],
                system_prompt="You are a helpful coding assistant."
            )
        
        async def execute(self, input_data):
            result = await self.think("Generate a Python function for...")
            return self.create_success_result({"code": result}, "Done!")
"""

import os
import asyncio
import time
import json
import logging
import hashlib
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from .llm_providers import (
    get_provider, 
    get_available_providers,
    chat_with_fallback,
    LLMMessage, 
    LLMResponse,
    BaseLLMProvider,
    ToolDefinition
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


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
    DATA_ANALYSIS = "data_analysis"
    REFACTORING = "refactoring"


@dataclass
class ExecutionMetrics:
    """Metrics from agent execution"""
    start_time: float = 0.0
    end_time: float = 0.0
    duration_ms: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0
    tokens_total: int = 0
    model_used: str = ""
    provider_used: str = ""
    retries: int = 0
    errors: List[str] = field(default_factory=list)


@dataclass
class MemoryEntry:
    """An entry in the agent's memory"""
    role: str
    content: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from agent execution"""
    success: bool
    data: Dict[str, Any]
    message: str
    error: Optional[str] = None
    artifacts: List[str] = field(default_factory=list)
    metrics: Optional[ExecutionMetrics] = None


class AgentMemory:
    """Memory system for maintaining conversation context"""
    
    def __init__(self, max_entries: int = 50, max_tokens: int = 8000):
        self.entries: List[MemoryEntry] = []
        self.max_entries = max_entries
        self.max_tokens = max_tokens
        self._token_estimate = 0
    
    def add(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add an entry to memory"""
        entry = MemoryEntry(
            role=role,
            content=content,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        self.entries.append(entry)
        self._token_estimate += len(content) // 4  # Rough estimate
        
        # Trim if too many entries
        while len(self.entries) > self.max_entries:
            removed = self.entries.pop(0)
            self._token_estimate -= len(removed.content) // 4
    
    def get_context(self, last_n: Optional[int] = None) -> List[LLMMessage]:
        """Get memory as LLM messages"""
        entries = self.entries[-last_n:] if last_n else self.entries
        return [LLMMessage(role=e.role, content=e.content) for e in entries]
    
    def clear(self):
        """Clear all memory"""
        self.entries = []
        self._token_estimate = 0
    
    def get_summary(self) -> str:
        """Get a summary of the memory for context compression"""
        if not self.entries:
            return ""
        return f"Previous conversation with {len(self.entries)} messages."


class BaseAgent(ABC):
    """
    Enterprise-grade base class for all SYNTHESIS agents.
    
    Features:
    - LLM provider integration with automatic fallback
    - Memory system for conversation context
    - Tool calling framework
    - Structured output parsing
    - Retry logic with exponential backoff
    - Comprehensive metrics and logging
    """

    def __init__(
        self,
        name: str,
        capabilities: List[AgentCapability],
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        max_memory_entries: int = 50,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        max_retries: int = 3
    ):
        self.name = name
        self.capabilities = capabilities
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.provider_name = provider or os.getenv("DEFAULT_PROVIDER", "openai")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        
        # Initialize components
        self.logger = logging.getLogger(f"Agent.{self.name}")
        self.memory = AgentMemory(max_entries=max_memory_entries)
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: List[ToolDefinition] = []
        self.metrics = ExecutionMetrics()
        
        # Get LLM provider
        self._provider: Optional[BaseLLMProvider] = None
        
        # Register default tools
        self._register_default_tools()
        
        self.logger.info(f"Agent {name} initialized with capabilities: {[c.value for c in capabilities]}")
    
    def _default_system_prompt(self) -> str:
        """Generate default system prompt based on capabilities"""
        caps = ", ".join([c.value for c in self.capabilities])
        return f"""You are {self.name}, an AI assistant specialized in: {caps}.

You provide clear, accurate, and helpful responses. When generating code:
- Write clean, production-ready code
- Include proper error handling
- Add helpful comments
- Follow best practices

Always structure your output clearly."""

    @property
    def provider(self) -> BaseLLMProvider:
        """Lazy load LLM provider"""
        if self._provider is None:
            self._provider = get_provider(self.provider_name)
        return self._provider
    
    def _register_default_tools(self):
        """Register default tools available to all agents"""
        # Subclasses can override to add more tools
        pass
    
    def register_tool(
        self, 
        name: str, 
        func: Callable, 
        description: str,
        parameters: Optional[Dict] = None
    ):
        """Register a tool that the agent can use"""
        self.tools[name] = func
        self.tool_definitions.append(ToolDefinition(
            name=name,
            description=description,
            parameters=parameters or {"type": "object", "properties": {}}
        ))
        self.logger.info(f"Tool registered: {name}")
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a registered tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found in {self.name}")
        
        self.log_thought(f"Executing tool: {tool_name}")
        try:
            if asyncio.iscoroutinefunction(self.tools[tool_name]):
                return await self.tools[tool_name](**kwargs)
            return self.tools[tool_name](**kwargs)
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            raise
    
    # =========================================================================
    # LLM Interaction Methods
    # =========================================================================
    
    async def think(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
        use_memory: bool = True
    ) -> str:
        """
        Send a prompt to the LLM and get a response.
        
        Args:
            prompt: The user prompt/question
            system_prompt: Override the agent's system prompt
            temperature: Override the agent's temperature
            max_tokens: Override max tokens
            json_mode: Request JSON-formatted response
            use_memory: Include conversation memory in context
        
        Returns:
            The LLM's response content
        """
        messages = []
        
        # Add system prompt
        sys_prompt = system_prompt or self.system_prompt
        if sys_prompt:
            messages.append(LLMMessage(role="system", content=sys_prompt))
        
        # Add memory context
        if use_memory and self.memory.entries:
            messages.extend(self.memory.get_context())
        
        # Add current prompt
        messages.append(LLMMessage(role="user", content=prompt))
        
        # Call LLM with retry logic
        response = await self._call_with_retry(
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            json_mode=json_mode
        )
        
        if response.success:
            # Add to memory
            self.memory.add("user", prompt)
            self.memory.add("assistant", response.content)
            
            # Update metrics
            self.metrics.tokens_input += response.usage.get("prompt_tokens", 0)
            self.metrics.tokens_output += response.usage.get("completion_tokens", 0)
            self.metrics.tokens_total += response.usage.get("total_tokens", 0)
            self.metrics.model_used = response.model
            self.metrics.provider_used = response.provider
            
            return response.content
        else:
            self.metrics.errors.append(response.error or "Unknown error")
            raise RuntimeError(f"LLM call failed: {response.error}")
    
    async def think_json(
        self,
        prompt: str,
        schema_hint: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get a JSON-structured response from the LLM.
        
        Args:
            prompt: The prompt
            schema_hint: Optional hint about expected JSON structure
            **kwargs: Additional arguments for think()
        
        Returns:
            Parsed JSON response as dictionary
        """
        if schema_hint:
            prompt = f"{prompt}\n\nRespond with valid JSON matching this structure:\n{schema_hint}"
        
        response = await self.think(prompt, json_mode=True, **kwargs)
        return self.parse_json_response(response)
    
    async def _call_with_retry(
        self,
        messages: List[LLMMessage],
        temperature: float,
        max_tokens: int,
        json_mode: bool = False
    ) -> LLMResponse:
        """Call LLM with exponential backoff retry"""
        last_error = ""
        
        for attempt in range(self.max_retries):
            try:
                response = await self.provider.chat(
                    messages=messages,
                    model=self.model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=self.tool_definitions if self.tool_definitions else None,
                    json_mode=json_mode
                )
                
                if response.success:
                    return response
                
                last_error = response.error or "Unknown error"
                self.metrics.retries += 1
                
            except Exception as e:
                last_error = str(e)
                self.metrics.retries += 1
            
            # Exponential backoff
            if attempt < self.max_retries - 1:
                wait_time = (2 ** attempt) + (0.1 * attempt)
                self.logger.warning(f"Retry {attempt + 1}/{self.max_retries} after {wait_time:.1f}s: {last_error}")
                await asyncio.sleep(wait_time)
        
        # Try fallback providers
        self.logger.warning(f"Primary provider failed, trying fallback...")
        return await chat_with_fallback(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=json_mode
        )
    
    # =========================================================================
    # Output Parsing
    # =========================================================================
    
    def parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks"""
        content = content.strip()
        
        # Try to extract from markdown code block
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            if end > start:
                content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            if end > start:
                content = content[start:end].strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            self.logger.warning(f"JSON parse error: {e}")
            # Try to find JSON object in content
            for i, char in enumerate(content):
                if char == '{':
                    depth = 1
                    for j in range(i + 1, len(content)):
                        if content[j] == '{':
                            depth += 1
                        elif content[j] == '}':
                            depth -= 1
                            if depth == 0:
                                try:
                                    return json.loads(content[i:j+1])
                                except:
                                    pass
                                break
            return {"raw_content": content, "parse_error": str(e)}
    
    # =========================================================================
    # Logging & Observability
    # =========================================================================
    
    def log_thought(self, thought: str):
        """Log agent's reasoning process"""
        self.logger.info(f"THOUGHT: {thought}")
        print(f"[{self.name}] 💭 {thought}")
    
    def log_action(self, action: str):
        """Log agent's action"""
        self.logger.info(f"ACTION: {action}")
        print(f"[{self.name}] ⚡ {action}")
    
    def log_result(self, result: str):
        """Log agent's result"""
        self.logger.info(f"RESULT: {result}")
        print(f"[{self.name}] ✅ {result}")
    
    def log_error(self, error: str):
        """Log an error"""
        self.logger.error(error)
        print(f"[{self.name}] ❌ {error}")
    
    # =========================================================================
    # Result Creation
    # =========================================================================
    
    def create_success_result(
        self, 
        data: Dict[str, Any], 
        message: str, 
        artifacts: Optional[List[str]] = None
    ) -> AgentResult:
        """Create a successful result"""
        self.log_result(message)
        return AgentResult(
            success=True,
            data=data,
            message=message,
            artifacts=artifacts or [],
            metrics=self.metrics
        )
    
    def create_error_result(self, message: str, error: str) -> AgentResult:
        """Create an error result"""
        self.log_error(f"{message}: {error}")
        return AgentResult(
            success=False,
            data={},
            message=message,
            error=error,
            metrics=self.metrics
        )
    
    # =========================================================================
    # Execution
    # =========================================================================
    
    def start_metrics(self):
        """Start tracking execution metrics"""
        self.metrics = ExecutionMetrics(start_time=time.time())
    
    def end_metrics(self):
        """Finalize execution metrics"""
        self.metrics.end_time = time.time()
        self.metrics.duration_ms = (self.metrics.end_time - self.metrics.start_time) * 1000
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute the agent's main task.
        Must be implemented by specific agents.
        
        Args:
            input_data: Input parameters for the agent
        
        Returns:
            AgentResult with success/failure and data
        """
        pass
    
    async def safe_execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute with comprehensive error handling"""
        self.start_metrics()
        self.log_thought(f"Starting execution with input: {list(input_data.keys())}")
        
        try:
            result = await self.execute(input_data)
            self.end_metrics()
            return result
        except Exception as e:
            self.end_metrics()
            self.log_error(f"Execution failed: {str(e)}")
            return self.create_error_result(
                f"{self.name} execution failed",
                str(e)
            )
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.capabilities
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "name": self.name,
            "capabilities": [c.value for c in self.capabilities],
            "provider": self.provider_name,
            "model": self.model or self.provider.default_model,
            "tools": list(self.tools.keys()),
            "memory_entries": len(self.memory.entries)
        }