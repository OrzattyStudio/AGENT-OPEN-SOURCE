# SYNTHESIS Agent Framework - Usage Guide

## 🚀 **Quick Start - Build Your First Agent**

### 1. Setup
```bash
# Clone or copy the framework
cp -r backend/AGENT_OPEN_SOURCE /your/project/
cd /your/project/
```

### 2. Create Your First Intelligent Agent
```python
# my_agent.py
from base_agent import BaseAgent, AgentCapability, AgentResult
from typing import Dict, Any
import openai  # Your AI library

class MyFrontendAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MyFrontendAgent",
            capabilities=[AgentCapability.FRONTEND_DEVELOPMENT, AgentCapability.CODE_GENERATION]
        )

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        # Your AI logic here - this is where the intelligence goes
        prompt = f"Generate React component for: {input_data.get('description', '')}"

        # Call your AI model (OpenAI, Claude, etc.)
        response = await self.call_ai_model(prompt)

        return self.create_success_result(
            data={
                "component_code": response,
                "framework": "React",
                "language": "TypeScript"
            },
            message="Frontend component generated successfully"
        )

    async def call_ai_model(self, prompt: str) -> str:
        # Your proprietary AI implementation
        # This is where SYNTHESIS's intelligence would go
        client = openai.Client(api_key="your-key")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
```

### 3. Use Your Agent
```python
# main.py
import asyncio
from my_agent import MyFrontendAgent

async def main():
    agent = MyFrontendAgent()

    result = await agent.safe_execute({
        "description": "A beautiful login form with validation",
        "requirements": ["responsive", "accessible", "modern design"]
    })

    if result.success:
        print("Generated component:", result.data["component_code"])
    else:
        print("Error:", result.error)

if __name__ == "__main__":
    asyncio.run(main())
```

## 🏗️ **Advanced Usage - Multi-Agent System**

### Coordinator Pattern
```python
# coordinator.py
from typing import List
import asyncio

class SimpleCoordinator:
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    async def execute_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        results = {}

        # Execute agents in sequence (basic orchestration)
        for agent in self.agents:
            if self._agent_can_handle(agent, task):
                result = await agent.safe_execute(task)
                results[agent.name] = result.data

        return results

    def _agent_can_handle(self, agent: BaseAgent, task: Dict) -> bool:
        # Simple capability matching
        required_caps = task.get("required_capabilities", [])
        return any(cap in [c.value for c in agent.capabilities] for cap in required_caps)
```

### Memory Management
```python
# The framework handles memory automatically
agent = MyAgent()

# Check memory usage
if agent.check_memory_limits():
    print("Memory OK")
else:
    print("Memory cleanup performed")

# Output is automatically sanitized
result = await agent.safe_execute(data)
# result.data is safe for logging/storage
```

## 🔧 **Framework Features You Get**

### Automatic Security
```python
# Input sanitization
sanitized = agent.sanitize_output(user_input)

# SQL injection prevention
# XSS prevention
# Sensitive data masking
```

### Memory Management
```python
# Automatic cleanup
await agent.cleanup_memory()

# Memory limits enforcement
agent.max_memory_mb = 100  # Custom limits
```

### Error Handling
```python
# Structured errors
try:
    result = await agent.safe_execute(data)
except Exception as e:
    structured_error = agent.create_structured_error(e)
    print(f"Error: {structured_error.message}")
```

## 🎯 **Building Intelligence (Your Part)**

### AI Integration Patterns
```python
class IntelligentAgent(BaseAgent):
    async def execute(self, input_data):
        # Pattern 1: Direct LLM call
        response = await self.call_llm(input_data)

        # Pattern 2: Chain of thought
        thoughts = await self.reason_step_by_step(input_data)

        # Pattern 3: Multi-step reasoning
        analysis = await self.analyze_requirements(input_data)
        design = await self.create_design(analysis)
        code = await self.generate_code(design)

        return self.create_success_result({
            "analysis": analysis,
            "design": design,
            "code": code
        })
```

### Custom Capabilities
```python
class SpecializedAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SpecializedAgent",
            capabilities=[
                AgentCapability.CODE_GENERATION,
                AgentCapability.SECURITY_ANALYSIS,
                # Add your custom capabilities
            ]
        )
```

## 🚀 **Scaling Up - Enterprise Patterns**

### Agent Registry
```python
class AgentRegistry:
    def __init__(self):
        self.agents = {}

    def register(self, agent: BaseAgent):
        self.agents[agent.name] = agent

    def get_agents_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        return [a for a in self.agents.values() if capability in a.capabilities]
```

### Workflow Orchestration
```python
class WorkflowEngine:
    async def execute_complex_workflow(self, workflow_config: Dict) -> Dict:
        # Parse workflow steps
        # Execute agents in order
        # Handle dependencies
        # Aggregate results
        # Error recovery
        pass
```

## 🔒 **Security Best Practices**

### Input Validation
```python
async def execute(self, input_data):
    # Validate input
    if not isinstance(input_data, dict):
        return self.create_error_result("Invalid input type")

    required_fields = ["description", "requirements"]
    for field in required_fields:
        if field not in input_data:
            return self.create_error_result(f"Missing required field: {field}")

    # Proceed with validated input
    return await self.process_validated_input(input_data)
```

### Output Sanitization
```python
def sanitize_code_output(self, code: str) -> str:
    # Remove dangerous patterns
    # Validate syntax
    # Check for security issues
    return sanitized_code
```

## 📊 **Monitoring & Observability**

### Metrics Tracking
```python
# Framework provides automatic metrics
result = await agent.safe_execute(data)

# Access execution metrics
metrics = result.metrics
print(f"Execution time: {metrics.duration_ms}ms")
print(f"Tokens used: {metrics.tokens_input + metrics.tokens_output}")
print(f"Memory used: {agent._memory_usage}MB")
```

### Logging
```python
# Structured logging included
agent.log_info("Agent started", task_id="123")
agent.log_error("Processing failed", error="timeout")
```

## 🎉 **Next Steps**

1. **Add Intelligence**: Implement your AI logic in the `execute` methods
2. **Build Coordination**: Create workflow engines for multi-agent tasks
3. **Add Specializations**: Extend capabilities for domain-specific tasks
4. **Scale Up**: Deploy multiple agents with load balancing

## 🤝 **Contributing**

This framework is MIT licensed. Contributions welcome:
- New agent skeletons
- Framework improvements
- Documentation enhancements
- Integration patterns

## 📞 **Support**

- **Documentation**: This guide and README.md
- **Community**: GitHub issues and discussions
- **Full Platform**: [synthesis.ai](https://synthesis.ai) for the complete AI-powered system

---

**Remember: The framework provides the architecture. You provide the intelligence.** 🧠✨