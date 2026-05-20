"""Global sanctions screening — OFAC + UN + EU + Korea STIC.

Due-diligence on a counterparty (person, organization, vessel, or wallet)
against the four public consolidated lists every regulated entity is
expected to screen against:

- OFAC SDN (US Treasury Specially Designated Nationals)
- UN Security Council consolidated list
- EU Financial Sanctions consolidated list
- Korea Strategic Trade Information Center (전략물자관리원)

Wallet addresses are also screened against OFAC's SDN crypto-address
subset. All four lists are public, no upstream key required.

Backed by /api/verify/sanctions/screen. Anti-mission #7-safe — uses only
publicly-published sanctions lists; never collects or stores queries.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="sanctions_screen",
        description=(
            "Screen a name, entity, or blockchain address against the OFAC "
            "SDN, UN consolidated, EU financial sanctions, and Korean "
            "Strategic Trade Information Center lists in one call. Returns "
            "per-list hits with similarity score, designation date, and "
            "source URL. Use before any onboarding, transfer, or contract "
            "execution touching a counterparty. Default sources cover the "
            "four major lists; restrict via `sources` to speed up."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 200,
                    "description": (
                        "Name (person/org), wallet address (0x... or btc), or "
                        "vessel name to screen. For wallets, lowercase Ethereum "
                        "addresses are canonicalized."
                    ),
                },
                "kind": {
                    "type": "string",
                    "enum": ["auto", "name", "address"],
                    "default": "auto",
                    "description": (
                        "Force interpretation: 'name' (person/org/vessel), "
                        "'address' (crypto wallet), or 'auto' (sniff from input)."
                    ),
                },
                "sources": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["ofac", "un", "eu", "kr_stic"],
                    },
                    "uniqueItems": True,
                    "default": ["ofac", "un", "eu", "kr_stic"],
                    "description": (
                        "Subset of lists to query. Omit to query all four. "
                        "'kr_stic' = 한국 전략물자관리원."
                    ),
                },
                "threshold": {
                    "type": "number",
                    "minimum": 0.5,
                    "maximum": 1.0,
                    "default": 0.85,
                    "description": (
                        "Similarity threshold for name matching (token-sort "
                        "ratio). 1.0 = exact, 0.85 = default fuzzy."
                    ),
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "sanctions_screen": lambda a: (
        "GET",
        "verify/sanctions/screen",
        {
            "query": a.get("query"),
            "kind": a.get("kind") or "auto",
            "sources": ",".join(a.get("sources") or ["ofac", "un", "eu", "kr_stic"]),
            "threshold": a.get("threshold") or 0.85,
        },
        None,
    ),
}
