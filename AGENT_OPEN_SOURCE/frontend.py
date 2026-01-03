"""
SYNTHESIS - FrontendAgent (Open Source Version)
Frontend development and UI implementation specialist
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentCapability, AgentResult

class FrontendAgent(BaseAgent):
    """
    FrontendAgent - Generates frontend components and standardized HTML structure.
    """

    def __init__(self):
        super().__init__(
            name="FrontendAgent",
            capabilities=[
                AgentCapability.FRONTEND_DEVELOPMENT, AgentCapability.CODE_GENERATION
            ]
        )
        self.register_tool("scaffold_component", self.scaffold_component, "Generates React/Vue/Vanilla JS component structure")
        self.register_tool("generate_html", self.generate_html, "Generates HTML5 boilerplate")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute frontend tasks.
        Input format:
        {
            "action": "scaffold_component" | "generate_html",
            "name": "ComponentName",
            "framework": "react" | "vue" | "vanilla"
        }
        """
        action = input_data.get("action")
        
        if action == "scaffold_component":
            name = input_data.get("name", "NewComponent")
            style = input_data.get("style", "css")
            framework = input_data.get("framework", "react")
            code = await self.execute_tool("scaffold_component", name=name, framework=framework, style=style)
            return self.create_success_result(
                data={"code": code, "type": "component"},
                message=f"Created {framework} component: {name}"
            )
            
        elif action == "generate_html":
            title = input_data.get("title", "App")
            code = await self.execute_tool("generate_html", title=title)
            return self.create_success_result(
                data={"code": code, "type": "html"},
                message=f"Generated HTML5 boilerplate for {title}"
            )
            
        else:
            return self.create_error_result("Unknown action", f"Action '{action}' is not supported")

    def scaffold_component(self, name: str, framework: str, style: str) -> Dict[str, str]:
        """Generate component files"""
        self.log_thought(f"Scaffolding {framework} component: {name}")
        
        files = {}
        if framework == "react":
            files[f"{name}.jsx"] = f"""import React from 'react';
import './{name}.{style}';

export const {name} = (props) => {{
  return (
    <div className="{name.lower()}-container">
      <h1>{name} Component</h1>
      {{props.children}}
    </div>
  );
}};
"""
            files[f"{name}.{style}"] = f".{name.lower()}-container {{ padding: 20px; border: 1px solid #ccc; }}"
            
        elif framework == "vue":
             files[f"{name}.vue"] = f"""<template>
  <div class="{name.lower()}">
    <h1>{name} Component</h1>
  </div>
</template>

<script>
export default {{
  name: '{name}'
}}
</script>

<style scoped>
.{name.lower()} {{
  padding: 20px;
}}
</style>
"""
        else:
            return {"error": "Framework not supported in this version"}
            
        return files

    def generate_html(self, title: str) -> str:
        """Generate HTML boilerplate"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="app"></div>
    <script src="main.js"></script>
</body>
</html>"""
