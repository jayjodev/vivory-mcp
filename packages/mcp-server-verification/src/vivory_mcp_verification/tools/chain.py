"""On-chain transaction audit lookup.

Vivory's `blockchain_audit` endpoint pulls a confirmed EVM transaction,
normalizes the receipt, builds a hash-chain over (tx, receipt, logs),
and Ed25519-signs the audit envelope with the same key Vivory uses for
its tool verification receipts. One Vivory pubkey ⇒ one trust anchor
across the entire verification cluster.

Supported chains: Ethereum, Arbitrum, Base, Optimism, Polygon (EVM
explorer parity with Vivory's `tools.vivory.app/blockchain-audit`).
Backed by /api/blockchain-audit/* on api.vivory.app. Etherscan v2 API
key is upstream-managed (no key required from the MCP client).
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="blockchain_audit_lookup",
        description=(
            "Fetch a confirmed EVM transaction and return a signed audit "
            "envelope: chain metadata, normalized tx + receipt, the "
            "computed hash chain over (raw_tx, raw_receipt, logs), and "
            "an Ed25519 signature over the canonical message. Use this "
            "when an agent needs to prove a specific tx happened on a "
            "specific chain at a specific block — the same envelope "
            "Vivory's `tools.vivory.app/blockchain-audit` UI renders. "
            "Returns 409 if tx is broadcast but not mined yet, 404 if "
            "the tx hash is unknown. Caches 10min."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "chain": {
                    "type": "string",
                    "enum": ["ethereum", "arbitrum", "base", "optimism", "polygon"],
                    "description": "EVM chain slug.",
                },
                "tx": {
                    "type": "string",
                    "pattern": "^0x[0-9a-fA-F]{64}$",
                    "description": "0x-prefixed 32-byte transaction hash.",
                },
            },
            "required": ["chain", "tx"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="blockchain_audit_chains",
        description=(
            "List the EVM chains supported by `blockchain_audit_lookup` — "
            "slug, chainId, label, block explorer base URL. Cheap discovery "
            "call for agents picking a chain dynamically."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    ),
    Tool(
        name="verify_contract_admin_activity",
        description=(
            "Detect recent admin activity on an EVM contract — owner "
            "transfers, role grants, pauses, upgrades. Scans the contract's "
            "tx history (last N days, default 30, max 365) via Etherscan v2, "
            "decodes events from common patterns (Ownable, AccessControl, "
            "Pausable, UUPS/Transparent proxies), and returns a chronological "
            "list of admin-flagged events with tx hash + block + decoded "
            "args. Empty list = no detected admin activity in window. Use "
            "before signing off on a contract as 'audited and stable'."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "chain": {
                    "type": "string",
                    "enum": ["ethereum", "arbitrum", "base", "optimism", "polygon"],
                },
                "contract": {
                    "type": "string",
                    "pattern": "^0x[0-9a-fA-F]{40}$",
                    "description": "0x-prefixed 20-byte contract address.",
                },
                "days": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 365,
                    "default": 30,
                    "description": "Lookback window in days.",
                },
            },
            "required": ["chain", "contract"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="verify_proxy_upgrade",
        description=(
            "Read the EIP-1967 implementation slot of a proxy contract and "
            "return the current implementation address + recent Upgraded "
            "events. For EIP-1967 proxies (UUPS, TransparentUpgradeable), "
            "the implementation lives at storage slot 0x360894...e103 — we "
            "read it via eth_getStorageAt and decode the address. Then we "
            "scan the proxy's logs for `Upgraded(address)` events to build "
            "the implementation history. Use when an agent is interacting "
            "with a contract that might be a proxy — knowing the current "
            "impl + whether it was recently upgraded is critical for trust."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "chain": {
                    "type": "string",
                    "enum": ["ethereum", "arbitrum", "base", "optimism", "polygon"],
                },
                "contract": {
                    "type": "string",
                    "pattern": "^0x[0-9a-fA-F]{40}$",
                    "description": "0x-prefixed proxy contract address.",
                },
            },
            "required": ["chain", "contract"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "blockchain_audit_lookup": lambda a: (
        "GET",
        "blockchain-audit/lookup",
        {"chain": a.get("chain"), "tx": a.get("tx")},
        None,
    ),
    "blockchain_audit_chains": lambda a: (
        "GET",
        "blockchain-audit/chains",
        None,
        None,
    ),
    "verify_contract_admin_activity": lambda a: (
        "GET",
        "blockchain-audit/contract/admin",
        {
            "chain": a.get("chain"),
            "contract": a.get("contract"),
            "days": a.get("days"),
        },
        None,
    ),
    "verify_proxy_upgrade": lambda a: (
        "GET",
        "blockchain-audit/contract/proxy",
        {"chain": a.get("chain"), "contract": a.get("contract")},
        None,
    ),
}
