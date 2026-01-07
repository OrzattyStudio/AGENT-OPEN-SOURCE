"""
SYNTHESIS - DatabaseAgent (Open Source Version)
Database design and optimization specialist
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentCapability, AgentResult

class DatabaseAgent(BaseAgent):
    """
    DatabaseAgent - Generates SQL schemas and queries.
    """

    def __init__(self):
        super().__init__(
            name="DatabaseAgent",
            capabilities=[
                AgentCapability.DATABASE_DESIGN, AgentCapability.BACKEND_DEVELOPMENT
            ]
        )
        self.register_tool("generate_schema_sql", self.generate_schema_sql, "Generates CREATE TABLE SQL based on fields")
        self.register_tool("generate_crud_queries", self.generate_crud_queries, "Generates CRUD SQL queries for a table")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute database tasks.
        Input:
        { "action": "generate_schema" | "generate_queries", "table_name": "...", "fields": {...} }
        """
        action = input_data.get("action")
        
        if action == "generate_schema":
            table = input_data.get("table_name", "mytable")
            fields = input_data.get("fields", {})
            sql = await self.execute_tool("generate_schema_sql", table=table, fields=fields)
            return self.create_success_result(
                data={"sql": sql},
                message=f"Generated schema for {table}"
            )

        elif action == "generate_queries":
            table = input_data.get("table_name", "mytable")
            sql = await self.execute_tool("generate_crud_queries", table=table)
            return self.create_success_result(
                data={"sql": sql},
                message=f"Generated CRUD queries for {table}"
            )
            
        else:
             return self.create_error_result("Unknown action", f"Action '{action}' not supported")

    def generate_schema_sql(self, table: str, fields: Dict[str, str]) -> str:
        """Generate CREATE TABLE SQL"""
        self.log_thought(f"Designing schema for table: {table}")
        
        lines = [f"CREATE TABLE {table} ("]
        lines.append("    id SERIAL PRIMARY KEY,")
        
        for name, type_ in fields.items():
            sql_type = "TEXT"
            if "int" in type_.lower(): sql_type = "INTEGER"
            if "bool" in type_.lower(): sql_type = "BOOLEAN"
            if "date" in type_.lower(): sql_type = "TIMESTAMP"
            lines.append(f"    {name} {sql_type},")
            
        # Remove trailing comma from last field
        lines[-1] = lines[-1].rstrip(',')
        lines.append(");")
        
        return "\n".join(lines)

    def generate_crud_queries(self, table: str) -> Dict[str, str]:
        """Generate basic CRUD queries"""
        self.log_thought(f"Generating CRUD queries for table: {table}")
        
        return {
            "create": f"INSERT INTO {table} (col1, col2) VALUES ($1, $2) RETURNING id;",
            "read": f"SELECT * FROM {table} WHERE id = $1;",
            "update": f"UPDATE {table} SET col1 = $1 WHERE id = $2;",
            "delete": f"DELETE FROM {table} WHERE id = $1;"
        }
