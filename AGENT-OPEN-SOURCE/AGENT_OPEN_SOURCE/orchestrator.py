"""
SYNTHESIS Open Source Agent Framework - Multi-Agent Orchestrator

Coordinates multiple agents to complete complex tasks.
Features:
- Agent selection based on capabilities
- Pipeline execution (sequential/parallel)
- Context passing between agents
- Error recovery and rollback

Usage:
    from orchestrator import Orchestrator
    
    orch = Orchestrator()
    result = await orch.run("Build a REST API for user management")
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List, Type
from dataclasses import dataclass, field
from enum import Enum

from .base_agent import BaseAgent, AgentResult, AgentCapability

logger = logging.getLogger("Orchestrator")


class ExecutionMode(Enum):
    """How to execute agents"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"


@dataclass
class AgentTask:
    """A task to be executed by an agent"""
    agent_name: str
    input_data: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    priority: int = 0


@dataclass
class PipelineResult:
    """Result from a pipeline execution"""
    success: bool
    results: Dict[str, AgentResult]
    total_duration_ms: float
    errors: List[str] = field(default_factory=list)


class AgentRegistry:
    """Registry of available agents"""
    
    def __init__(self):
        self._agents: Dict[str, Type[BaseAgent]] = {}
        self._instances: Dict[str, BaseAgent] = {}
    
    def register(self, name: str, agent_class: Type[BaseAgent]):
        """Register an agent class"""
        self._agents[name] = agent_class
        logger.info(f"Registered agent: {name}")
    
    def get(self, name: str) -> BaseAgent:
        """Get an agent instance by name"""
        if name not in self._instances:
            if name not in self._agents:
                raise ValueError(f"Unknown agent: {name}")
            self._instances[name] = self._agents[name]()
        return self._instances[name]
    
    def get_by_capability(self, capability: AgentCapability) -> List[str]:
        """Get agents that have a specific capability"""
        result = []
        for name, agent_class in self._agents.items():
            agent = self.get(name)
            if agent.has_capability(capability):
                result.append(name)
        return result
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        return [
            {"name": name, "class": cls.__name__}
            for name, cls in self._agents.items()
        ]


class Orchestrator:
    """
    Orchestrates multiple agents to complete complex tasks.
    
    The orchestrator:
    1. Analyzes the task to determine required capabilities
    2. Selects appropriate agents
    3. Creates an execution plan
    4. Executes agents (sequential or parallel)
    5. Passes context between agents
    6. Handles errors and retries
    """
    
    def __init__(self, registry: Optional[AgentRegistry] = None):
        self.registry = registry or AgentRegistry()
        self.context: Dict[str, Any] = {}
        self.execution_history: List[Dict] = []
        self.logger = logging.getLogger("Orchestrator")
    
    def register_agent(self, name: str, agent_class: Type[BaseAgent]):
        """Register an agent with the orchestrator"""
        self.registry.register(name, agent_class)
    
    async def run(
        self,
        task: str,
        agents: Optional[List[str]] = None,
        mode: ExecutionMode = ExecutionMode.SEQUENTIAL,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> PipelineResult:
        """
        Run a task using the specified agents.
        
        Args:
            task: The task description
            agents: List of agent names to use (auto-select if None)
            mode: Execution mode (sequential, parallel, pipeline)
            initial_context: Initial context data
        
        Returns:
            PipelineResult with all agent results
        """
        start_time = time.time()
        self.context = initial_context or {}
        self.context["task"] = task
        
        results: Dict[str, AgentResult] = {}
        errors: List[str] = []
        
        # Get agents to execute
        if agents is None:
            agents = self._auto_select_agents(task)
        
        self.logger.info(f"Running task with agents: {agents}")
        print(f"\n🚀 Orchestrator starting task with {len(agents)} agents")
        print(f"📋 Task: {task[:100]}...")
        
        try:
            if mode == ExecutionMode.PARALLEL:
                results = await self._run_parallel(agents)
            else:
                results = await self._run_sequential(agents)
            
            # Check for failures
            for name, result in results.items():
                if not result.success:
                    errors.append(f"{name}: {result.error}")
            
        except Exception as e:
            errors.append(str(e))
            self.logger.error(f"Orchestration failed: {e}")
        
        duration = (time.time() - start_time) * 1000
        
        success = len(errors) == 0
        print(f"\n{'✅' if success else '❌'} Orchestration {'completed' if success else 'failed'} in {duration:.0f}ms")
        
        return PipelineResult(
            success=success,
            results=results,
            total_duration_ms=duration,
            errors=errors
        )
    
    async def _run_sequential(self, agents: List[str]) -> Dict[str, AgentResult]:
        """Run agents sequentially, passing context between them"""
        results = {}
        
        for i, agent_name in enumerate(agents):
            print(f"\n[{i+1}/{len(agents)}] Running {agent_name}...")
            
            try:
                agent = self.registry.get(agent_name)
                
                # Build input from context
                input_data = {
                    "task": self.context.get("task", ""),
                    "context": self.context,
                    "previous_results": results
                }
                
                # Execute agent
                result = await agent.safe_execute(input_data)
                results[agent_name] = result
                
                # Update context with results
                if result.success:
                    self.context[f"{agent_name}_output"] = result.data
                    print(f"   ✅ {agent_name}: {result.message}")
                else:
                    print(f"   ❌ {agent_name}: {result.error}")
                
                # Record execution
                self.execution_history.append({
                    "agent": agent_name,
                    "success": result.success,
                    "timestamp": time.time()
                })
                
            except Exception as e:
                self.logger.error(f"Agent {agent_name} failed: {e}")
                results[agent_name] = AgentResult(
                    success=False,
                    data={},
                    message=f"Agent execution failed",
                    error=str(e)
                )
        
        return results
    
    async def _run_parallel(self, agents: List[str]) -> Dict[str, AgentResult]:
        """Run agents in parallel"""
        async def run_agent(agent_name: str) -> tuple:
            try:
                agent = self.registry.get(agent_name)
                input_data = {
                    "task": self.context.get("task", ""),
                    "context": self.context
                }
                result = await agent.safe_execute(input_data)
                return agent_name, result
            except Exception as e:
                return agent_name, AgentResult(
                    success=False,
                    data={},
                    message="Agent execution failed",
                    error=str(e)
                )
        
        tasks = [run_agent(name) for name in agents]
        completed = await asyncio.gather(*tasks)
        
        return {name: result for name, result in completed}
    
    def _auto_select_agents(self, task: str) -> List[str]:
        """Automatically select agents based on task description"""
        task_lower = task.lower()
        selected = []
        
        # Simple keyword matching for agent selection
        capability_keywords = {
            AgentCapability.CODE_GENERATION: ["code", "function", "class", "implement", "create", "build"],
            AgentCapability.FRONTEND_DEVELOPMENT: ["frontend", "ui", "react", "vue", "html", "css", "component"],
            AgentCapability.BACKEND_DEVELOPMENT: ["backend", "api", "server", "endpoint", "database"],
            AgentCapability.TESTING: ["test", "testing", "unit test", "integration"],
            AgentCapability.SECURITY_ANALYSIS: ["security", "vulnerability", "auth", "permission"],
            AgentCapability.DOCUMENTATION: ["docs", "documentation", "readme", "comment"],
            AgentCapability.ARCHITECTURE: ["architecture", "design", "structure", "plan"]
        }
        
        for capability, keywords in capability_keywords.items():
            if any(kw in task_lower for kw in keywords):
                agents = self.registry.get_by_capability(capability)
                selected.extend(agents)
        
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for agent in selected:
            if agent not in seen:
                seen.add(agent)
                unique.append(agent)
        
        return unique if unique else list(self.registry._agents.keys())[:3]
    
    def get_context(self) -> Dict[str, Any]:
        """Get current execution context"""
        return self.context.copy()
    
    def clear_context(self):
        """Clear execution context"""
        self.context = {}
        self.execution_history = []


# Global orchestrator instance
_orchestrator: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    """Get the global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
