"""
SYNTHESIS Open Source Agent Framework

Enterprise-grade multi-agent framework for autonomous software development.

Quick Start:
    from AGENT_OPEN_SOURCE import FrontendAgent, BackendAgent, get_orchestrator
    
    # Single agent
    agent = FrontendAgent()
    result = await agent.safe_execute({"task": "Create a button component"})
    
    # Multi-agent orchestration
    orch = get_orchestrator()
    orch.register_agent("frontend", FrontendAgent)
    orch.register_agent("backend", BackendAgent)
    result = await orch.run("Build a user profile page with API")

Features:
    - LLM providers: OpenAI, Anthropic, Google, Groq, Ollama
    - Multi-agent orchestration
    - Memory system for context
    - Tool calling framework
    - Structured output parsing
    - Retry with fallback
"""

__version__ = "1.0.0"
__author__ = "SYNTHESIS"

# Core exports
from .base_agent import BaseAgent, AgentCapability, AgentResult
from .llm_providers import (
    get_provider,
    get_available_providers,
    chat_with_fallback,
    LLMMessage,
    LLMResponse,
    ProviderType
)
from .orchestrator import Orchestrator, get_orchestrator
from .config import Config

# Agent exports
from .frontend import FrontendAgent
from .backend import BackendAgent

__all__ = [
    # Core
    "BaseAgent",
    "AgentCapability", 
    "AgentResult",
    # LLM
    "get_provider",
    "get_available_providers",
    "chat_with_fallback",
    "LLMMessage",
    "LLMResponse",
    "ProviderType",
    # Orchestration
    "Orchestrator",
    "get_orchestrator",
    # Config
    "Config",
    # Agents
    "FrontendAgent",
    "BackendAgent"
]
