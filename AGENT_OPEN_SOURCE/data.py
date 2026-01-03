"""
SYNTHESIS - DataAgent (Open Source Version)
Data engineering and pipeline management
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class DataAgent(BaseAgent):
    """
    DataAgent - Generates ETL pipeline scripts.
    """

    def __init__(self):
        super().__init__(
            name="DataAgent",
            capabilities=[
                AgentCapability.DATA_ANALYSIS, AgentCapability.BACKEND_DEVELOPMENT
            ]
        )
        self.register_tool("generate_etl", self.generate_etl, "Generates basic ETL script")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute data tasks.
        Input: { "action": "etl", "source": "csv", "dest": "postgres" }
        """
        action = input_data.get("action")
        
        if action == "etl":
            source = input_data.get("source", "csv")
            dest = input_data.get("dest", "db")
            code = await self.execute_tool("generate_etl", source=source, dest=dest)
            return self.create_success_result(
                data={"code": code},
                message=f"Generated ETL from {source} to {dest}"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def generate_etl(self, source: str, dest: str) -> str:
        """Generate ETL Script"""
        self.log_thought(f"Designing ETL pipeline: {source} -> {dest}")
        return f"""import pandas as pd
from sqlalchemy import create_engine

# Extract
data = pd.read_{source}('source_file.{source}')

# Transform
data['processed'] = True

# Load
engine = create_engine('postgresql://user:pass@localhost:5432/db')
data.to_sql('destination_table', engine, if_exists='replace')
"""
