"""
SYNTHESIS - BackendAgent (Enterprise Open Source Version)

Backend development specialist for APIs, databases, and server-side logic.

Usage:
    from AGENT_OPEN_SOURCE import BackendAgent
    
    agent = BackendAgent()
    result = await agent.safe_execute({
        "task": "Create a REST API for user authentication with JWT"
    })
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentCapability, AgentResult


class BackendAgent(BaseAgent):
    """
    BackendAgent - Enterprise-grade backend development specialist.
    
    Capabilities:
    - REST API design and implementation
    - Database schema design
    - Authentication/Authorization
    - Server-side logic
    - API documentation
    """

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        super().__init__(
            name="BackendAgent",
            capabilities=[
                AgentCapability.BACKEND_DEVELOPMENT,
                AgentCapability.API_DESIGN,
                AgentCapability.DATABASE_DESIGN,
                AgentCapability.CODE_GENERATION
            ],
            system_prompt=self._create_system_prompt(),
            provider=provider,
            model=model
        )
        
        # Register tools
        self.register_tool(
            "generate_api_endpoint",
            self.generate_api_endpoint,
            "Generate a REST API endpoint",
            {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]},
                    "framework": {"type": "string", "enum": ["fastapi", "express", "flask", "django"]}
                }
            }
        )
        
        self.register_tool(
            "generate_database_schema",
            self.generate_database_schema,
            "Generate database schema/models",
            {
                "type": "object",
                "properties": {
                    "tables": {"type": "array", "items": {"type": "string"}},
                    "orm": {"type": "string", "enum": ["sqlalchemy", "prisma", "mongoose", "typeorm"]}
                }
            }
        )
    
    def _create_system_prompt(self) -> str:
        return """You are BackendAgent, an expert backend developer specializing in server-side development.

Your expertise:
- REST API design (FastAPI, Express, Flask, Django)
- Database design (PostgreSQL, MySQL, MongoDB)
- Authentication (JWT, OAuth, Sessions)
- Security best practices
- Performance optimization
- Caching strategies
- Message queues

When generating code:
1. Write clean, production-ready code
2. Include proper error handling
3. Add input validation
4. Implement security best practices
5. Add API documentation (OpenAPI/Swagger)
6. Include database migrations when needed

Always respond with JSON containing:
{
    "files": [
        {"path": "filename.ext", "content": "code here", "type": "python|javascript|sql"}
    ],
    "explanation": "Brief explanation of generated code",
    "api_endpoints": [
        {"method": "GET", "path": "/api/resource", "description": "..."}
    ]
}"""

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute backend generation task"""
        task = input_data.get("task", "")
        context = input_data.get("context", {})
        
        self.log_thought(f"Analyzing backend task: {task[:100]}...")
        
        # Determine framework
        framework = self._detect_framework(task, context)
        database = self._detect_database(task, context)
        
        prompt = f"""Generate backend code for the following task:

TASK: {task}

Framework: {framework}
Database: {database}

Generate complete, production-ready code including:
1. API endpoints with proper routing
2. Database models/schemas
3. Business logic
4. Error handling
5. Input validation
6. Authentication if needed

Respond with valid JSON containing the files and API documentation."""

        try:
            result = await self.think_json(prompt)
            
            files = result.get("files", [])
            explanation = result.get("explanation", "Backend code generated")
            endpoints = result.get("api_endpoints", [])
            
            self.log_result(f"Generated {len(files)} files with {len(endpoints)} endpoints")
            
            return self.create_success_result(
                data={
                    "files": files,
                    "framework": framework,
                    "database": database,
                    "api_endpoints": endpoints,
                    "explanation": explanation
                },
                message=f"Generated {len(files)} backend files using {framework}",
                artifacts=[f.get("path", "") for f in files]
            )
            
        except Exception as e:
            return self.create_error_result(
                "Backend generation failed",
                str(e)
            )
    
    def _detect_framework(self, task: str, context: Dict) -> str:
        """Detect which framework to use"""
        task_lower = task.lower()
        
        if "fastapi" in task_lower or "fast api" in task_lower:
            return "fastapi"
        elif "express" in task_lower or "node" in task_lower:
            return "express"
        elif "flask" in task_lower:
            return "flask"
        elif "django" in task_lower:
            return "django"
        
        return context.get("framework", "fastapi")
    
    def _detect_database(self, task: str, context: Dict) -> str:
        """Detect which database to use"""
        task_lower = task.lower()
        
        if "mongodb" in task_lower or "mongo" in task_lower:
            return "mongodb"
        elif "mysql" in task_lower:
            return "mysql"
        elif "sqlite" in task_lower:
            return "sqlite"
        
        return context.get("database", "postgresql")
    
    def generate_api_endpoint(
        self,
        name: str,
        method: str = "GET",
        framework: str = "fastapi"
    ) -> Dict[str, str]:
        """Generate an API endpoint"""
        self.log_action(f"Generating {method} endpoint: {name}")
        
        if framework == "fastapi":
            return {
                f"{name}.py": f'''from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class {name.title()}Request(BaseModel):
    # Add request fields here
    pass

class {name.title()}Response(BaseModel):
    id: str
    # Add response fields here

@router.{method.lower()}("/{name}")
async def {name}_endpoint(request: {name.title()}Request = None):
    """
    {name.title()} endpoint
    
    Returns:
        {name.title()}Response
    """
    try:
        # Implement logic here
        return {{"message": "Success", "id": "123"}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''
            }
        
        elif framework == "express":
            return {
                f"{name}.js": f'''const express = require('express');
const router = express.Router();

/**
 * {method} /{name}
 * @description {name.title()} endpoint
 */
router.{method.lower()}('/{name}', async (req, res) => {{
    try {{
        // Implement logic here
        res.json({{ message: 'Success', id: '123' }});
    }} catch (error) {{
        res.status(500).json({{ error: error.message }});
    }}
}});

module.exports = router;
'''
            }
        
        return {"error": f"Framework {framework} not supported"}
    
    def generate_database_schema(
        self,
        tables: List[str],
        orm: str = "sqlalchemy"
    ) -> Dict[str, str]:
        """Generate database schema"""
        self.log_action(f"Generating schema for tables: {tables}")
        
        if orm == "sqlalchemy":
            models = []
            for table in tables:
                models.append(f'''
class {table.title()}(Base):
    __tablename__ = "{table.lower()}"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Add more columns here
''')
            
            return {
                "models.py": f'''from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()
{"".join(models)}
'''
            }
        
        return {"error": f"ORM {orm} not supported"}
