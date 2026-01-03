"""
SYNTHESIS - BackendAgent (Open Source Version)
Backend development and server-side logic specialist
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentCapability, AgentResult

class BackendAgent(BaseAgent):
    """
    BackendAgent - Generates backend code scaffolding and data models using best-practice templates.
    """

    def __init__(self):
        super().__init__(
            name="BackendAgent",
            capabilities=[
                AgentCapability.BACKEND_DEVELOPMENT, AgentCapability.API_DESIGN
            ]
        )
        self.register_tool("generate_api_scaffold", self.generate_api_scaffold, "Generates Flask or FastAPI boilerplates")
        self.register_tool("create_model", self.create_model, "Generates Pydantic or SQLAlchemy models")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute backend tasks based on input.
        Input format expected: 
        {
            "action": "scaffold_api" | "create_model",
            ...params
        }
        """
        action = input_data.get("action")
        
        if action == "scaffold_api":
            framework = input_data.get("framework", "fastapi")
            name = input_data.get("project_name", "app")
            code = await self.execute_tool("generate_api_scaffold", framework=framework, name=name)
            return self.create_success_result(
                data={"code": code, "type": "scaffold"},
                message=f"Generated {framework} scaffold for {name}"
            )
            
        elif action == "create_model":
            name = input_data.get("model_name", "MyModel")
            fields = input_data.get("fields", {})
            model_type = input_data.get("type", "pydantic")
            code = await self.execute_tool("create_model", name=name, fields=fields, model_type=model_type)
            return self.create_success_result(
                data={"code": code},
                message=f"Generated {model_type} model for {name}"
            )
            
        else:
            return self.create_error_result("Unknown action", f"Action '{action}' not supported")

    def generate_api_scaffold(self, framework: str, name: str) -> str:
        """Generate API boilerplate code"""
        self.log_thought(f"Generating scaffolding for {framework}...")
        
        if framework.lower() == "fastapi":
            return f'''
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="{name}")

@app.get("/")
def read_root():
    return {{"message": "Welcome to {name} API"}}

@app.get("/health")
def health_check():
    return {{"status": "healthy"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        elif framework.lower() == "flask":
            return f'''
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify(message="Welcome to {name} API")

@app.route("/health")
def health():
    return jsonify(status="healthy")

if __name__ == "__main__":
    app.run(debug=True)
'''
        else:
            raise ValueError(f"Framework {framework} not supported")

    def create_model(self, name: str, fields: Dict[str, str], model_type: str) -> str:
        """Generate data model code"""
        self.log_thought(f"Designing data model {name} ({model_type})")
        
        lines = []
        if model_type == "pydantic":
            lines.append("from pydantic import BaseModel")
            lines.append("from typing import Optional, List")
            lines.append("")
            lines.append(f"class {name}(BaseModel):")
            if not fields:
                lines.append("    pass")
            for field, type_ in fields.items():
                lines.append(f"    {field}: {type_}")
                
        elif model_type == "sqlalchemy":
            lines.append("from sqlalchemy import Column, Integer, String, Boolean")
            lines.append("from sqlalchemy.ext.declarative import declarative_base")
            lines.append("")
            lines.append("Base = declarative_base()")
            lines.append("")
            lines.append(f"class {name}(Base):")
            lines.append(f"    __tablename__ = '{name.lower()}s'")
            lines.append("    id = Column(Integer, primary_key=True)")
            for field, type_ in fields.items():
                 # Simple mapping for demo
                sql_type = "String"
                if "int" in type_.lower(): sql_type = "Integer"
                if "bool" in type_.lower(): sql_type = "Boolean"
                lines.append(f"    {field} = Column({sql_type})")
        
        return "\n".join(lines)
