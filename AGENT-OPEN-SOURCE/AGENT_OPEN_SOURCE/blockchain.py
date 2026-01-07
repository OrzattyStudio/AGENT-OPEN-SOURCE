"""
SYNTHESIS - BlockchainAgent (Open Source Version)
Smart contract and DApp development
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability, AgentResult

class BlockchainAgent(BaseAgent):
    """
    BlockchainAgent - Generates Solidity Smart Contracts.
    """

    def __init__(self):
        super().__init__(
            name="BlockchainAgent",
            capabilities=[
                AgentCapability.CODE_GENERATION, AgentCapability.SECURITY_ANALYSIS
            ]
        )
        self.register_tool("generate_contract", self.generate_contract, "Generates ERC-20/721 Token Contracts")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute blockchain tasks.
        Input: { "action": "generate", "standard": "erc20", "name": "MyToken", "symbol": "MTK" }
        """
        action = input_data.get("action")
        
        if action == "generate":
            standard = input_data.get("standard", "erc20")
            name = input_data.get("name", "Token")
            symbol = input_data.get("symbol", "TKN")
            code = await self.execute_tool("generate_contract", standard=standard, name=name, symbol=symbol)
            return self.create_success_result(
                data={"code": code},
                message=f"Generated {standard} contract"
            )
        return self.create_error_result("Unknown action", f"Action {action} not supported")

    def generate_contract(self, standard: str, name: str, symbol: str) -> str:
        """Generate Solidity code"""
        self.log_thought(f"Writing {standard} smart contract for {name}")
        
        if standard == "erc20":
            return f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract {name} is ERC20 {{
    constructor() ERC20("{name}", "{symbol}") {{
        _mint(msg.sender, 1000000 * 10 ** decimals());
    }}
}}
"""
        return "// Standard not supported"
