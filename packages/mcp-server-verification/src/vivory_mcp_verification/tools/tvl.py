"""DefiLlama crypto TVL verification tools.

DefiLlama publishes daily TVL (total value locked) snapshots across
all major DeFi protocols and chains with a publicly auditable
methodology — the de-facto industry source-of-truth that crypto
publications, analyst reports, and on-chain agents already cite. Vivory
wraps the open API into a citation surface so an LLM about to assert
'X protocol has $Y TVL' can self-check before publishing.

Backed by /api/verify/tvl/protocol + /api/verify/tvl/chain.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="verify_protocol_tvl",
        description=(
            "Resolve a DefiLlama protocol slug to current TVL + per-chain "
            "breakdown + 1d/7d/30d change percentages + market cap + "
            "category. Use before an LLM cites a protocol's TVL — slug "
            "examples: 'aave', 'lido', 'uniswap', 'makerdao'."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "slug": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 80,
                    "description": "DefiLlama protocol slug (kebab-case, lowercase).",
                },
            },
            "required": ["slug"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="verify_chain_tvl",
        description=(
            "Return the current TVL for an entire chain (sum across all "
            "protocols on that chain) plus 30-day daily history. Use for "
            "chain-level claim verification — e.g. 'Arbitrum TVL hit $X "
            "on date Y'. Chain examples: 'Ethereum', 'Arbitrum', "
            "'Solana', 'Base'."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "chain": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 40,
                    "description": "DefiLlama chain name (capitalized, e.g. 'Ethereum').",
                },
            },
            "required": ["chain"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_protocol_tvl": lambda a: ("GET", "verify/tvl/protocol", {"slug": a.get("slug")}, None),
    "verify_chain_tvl": lambda a: ("GET", "verify/tvl/chain", {"chain": a.get("chain")}, None),
}
