"""
SYNTHESIS - FrontendAgent (Enterprise Open Source Version)

Frontend development and UI implementation specialist.
Generates React, Vue, Angular, and Vanilla JS components.

Usage:
    from AGENT_OPEN_SOURCE import FrontendAgent
    
    agent = FrontendAgent()
    result = await agent.safe_execute({
        "task": "Create a responsive navigation component with dark mode toggle"
    })
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentCapability, AgentResult


class FrontendAgent(BaseAgent):
    """
    FrontendAgent - Enterprise-grade frontend development specialist.
    
    Capabilities:
    - React/Vue/Angular component generation
    - Responsive CSS/Tailwind styling
    - Accessibility compliance
    - Modern UI patterns
    """

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        super().__init__(
            name="FrontendAgent",
            capabilities=[
                AgentCapability.FRONTEND_DEVELOPMENT,
                AgentCapability.CODE_GENERATION
            ],
            system_prompt=self._create_system_prompt(),
            provider=provider,
            model=model
        )
        
        # Register tools
        self.register_tool(
            "scaffold_component",
            self.scaffold_component,
            "Generate component structure for React/Vue/Vanilla",
            {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Component name"},
                    "framework": {"type": "string", "enum": ["react", "vue", "vanilla"]},
                    "style": {"type": "string", "enum": ["css", "tailwind", "scss"]}
                }
            }
        )
    
    def _create_system_prompt(self) -> str:
        return """You are FrontendAgent, an expert frontend developer specializing in modern web development.

Your expertise:
- React (hooks, context, components)
- Vue.js (composition API, components)
- Vanilla JavaScript (ES6+, DOM manipulation)
- CSS/SCSS/Tailwind styling
- Responsive design
- Accessibility (WCAG compliance)
- Performance optimization

When generating code:
1. Write clean, production-ready code
2. Include proper TypeScript types when appropriate
3. Add accessibility attributes (aria-*, role)
4. Use semantic HTML elements
5. Implement responsive design
6. Add helpful comments

Always respond with JSON containing:
{
    "files": [
        {"path": "filename.ext", "content": "code here", "type": "react|vue|html|css|js"}
    ],
    "explanation": "Brief explanation of generated code"
}"""

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute frontend generation task"""
        task = input_data.get("task", "")
        context = input_data.get("context", {})
        
        self.log_thought(f"Analyzing frontend task: {task[:100]}...")
        
        # Determine framework from context or task
        framework = self._detect_framework(task, context)
        
        # Generate the frontend code
        prompt = f"""Generate frontend code for the following task:

TASK: {task}

Framework: {framework}

Generate complete, production-ready code. Include:
1. Main component/page code
2. Styling (CSS/Tailwind)
3. Any helper functions needed

Respond with valid JSON containing the files."""

        try:
            result = await self.think_json(prompt)
            
            files = result.get("files", [])
            explanation = result.get("explanation", "Frontend code generated")
            
            self.log_result(f"Generated {len(files)} files")
            
            return self.create_success_result(
                data={
                    "files": files,
                    "framework": framework,
                    "explanation": explanation
                },
                message=f"Generated {len(files)} frontend files using {framework}",
                artifacts=[f.get("path", "") for f in files]
            )
            
        except Exception as e:
            return self.create_error_result(
                "Frontend generation failed",
                str(e)
            )
    
    def _detect_framework(self, task: str, context: Dict) -> str:
        """Detect which framework to use based on task and context"""
        task_lower = task.lower()
        
        if "react" in task_lower or "jsx" in task_lower:
            return "react"
        elif "vue" in task_lower:
            return "vue"
        elif "angular" in task_lower:
            return "angular"
        elif "vanilla" in task_lower or "plain" in task_lower or "html" in task_lower:
            return "vanilla"
        
        # Check context for existing framework
        if context.get("framework"):
            return context["framework"]
        
        # Default to React
        return "react"
    
    def scaffold_component(
        self, 
        name: str, 
        framework: str = "react",
        style: str = "css"
    ) -> Dict[str, str]:
        """Generate component scaffold"""
        self.log_action(f"Scaffolding {framework} component: {name}")
        
        files = {}
        
        if framework == "react":
            files[f"{name}.tsx"] = f'''import React from 'react';
import './{name}.{style}';

interface {name}Props {{
  className?: string;
  children?: React.ReactNode;
}}

export const {name}: React.FC<{name}Props> = ({{ className = '', children }}) => {{
  return (
    <div className={{`{name.lower()}-container ${{className}}`}}>
      <h2>{name}</h2>
      {{children}}
    </div>
  );
}};

export default {name};
'''
            files[f"{name}.{style}"] = f'''.{name.lower()}-container {{
  padding: 1rem;
  border-radius: 0.5rem;
  background: var(--bg-secondary, #f5f5f5);
}}

.{name.lower()}-container h2 {{
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
}}
'''
        
        elif framework == "vue":
            files[f"{name}.vue"] = f'''<template>
  <div :class="['{name.lower()}-container', className]">
    <h2>{name}</h2>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{{
  className?: string;
}}>();
</script>

<style scoped>
.{name.lower()}-container {{
  padding: 1rem;
  border-radius: 0.5rem;
  background: var(--bg-secondary, #f5f5f5);
}}

.{name.lower()}-container h2 {{
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
}}
</style>
'''
        
        else:  # vanilla
            files[f"{name.lower()}.html"] = f'''<div class="{name.lower()}-container" id="{name.lower()}">
  <h2>{name}</h2>
  <div class="{name.lower()}-content"></div>
</div>
'''
            files[f"{name.lower()}.css"] = f'''.{name.lower()}-container {{
  padding: 1rem;
  border-radius: 0.5rem;
  background: var(--bg-secondary, #f5f5f5);
}}

.{name.lower()}-container h2 {{
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
}}
'''
            files[f"{name.lower()}.js"] = f'''class {name} {{
  constructor(element) {{
    this.element = element;
    this.init();
  }}

  init() {{
    console.log('{name} initialized');
  }}
}}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {{
  const container = document.getElementById('{name.lower()}');
  if (container) {{
    new {name}(container);
  }}
}});
'''
        
        return files
