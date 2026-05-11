"""GLEIF Legal Entity Identifier tools.

LEI (ISO 17442) is the corporate counterpart of DOI: a 20-char globally-
unique identifier issued by the LEI ROC. Vivory wraps GLEIF's public API
into entity-side citation trail: LEI in, canonical legal name + addresses
+ corporate hierarchy out — useful for verifying claims like
'X is a subsidiary of Y' or 'Z filed under jurisdiction K'.

Backed by /api/verify/entity/* on api.vivory.app. GLEIF is free public
infrastructure — Vivory only normalizes the JSON:API response.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_LEI = {
    "type": "string",
    "minLength": 20,
    "maxLength": 20,
    "pattern": "^[A-Z0-9]{18}[0-9]{2}$",
    "description": "ISO 17442 Legal Entity Identifier — 20-char alphanumeric.",
}

TOOLS: list[Tool] = [
    Tool(
        name="verify_lei",
        description=(
            "Resolve a Legal Entity Identifier to the canonical record: "
            "legal name, jurisdiction, legal + headquarters addresses, "
            "registration status (issued / lapsed / retired), and managing "
            "Local Operating Unit. Use as the default first call on any "
            "organization an LLM is about to cite — confirms the legal "
            "entity exists and surfaces its current registration state."
        ),
        inputSchema={
            "type": "object",
            "properties": {"lei": _LEI},
            "required": ["lei"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="entity_search",
        description=(
            "Fuzzy search GLEIF by legal name. Returns up to `limit` "
            "candidate LEIs with their canonical legal name + jurisdiction. "
            "Use when the agent has a corporate name (e.g. 'BlackRock Inc') "
            "but no LEI yet — pick the matching candidate, then call "
            "verify_lei or entity_relationships to drill in."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 2, "maxLength": 200},
                "country": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 2,
                    "description": "Optional ISO 3166-1 alpha-2 country filter (e.g. 'US', 'KR').",
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="entity_relationships",
        description=(
            "Return direct parent + ultimate parent + direct children for "
            "an LEI. The corporate-hierarchy citation trail — useful for "
            "verifying claims like 'X is a subsidiary of Y' or 'Z's "
            "ultimate parent is W'. Limited to direct children up to 20 "
            "(GLEIF page-size). Heavy call — caches 24h on the gateway."
        ),
        inputSchema={
            "type": "object",
            "properties": {"lei": _LEI},
            "required": ["lei"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_lei": lambda a: ("GET", "verify/entity/lei", {"lei": a.get("lei")}, None),
    "entity_search": lambda a: (
        "GET",
        "verify/entity/search",
        {"name": a.get("name"), "country": a.get("country"), "limit": a.get("limit")},
        None,
    ),
    "entity_relationships": lambda a: (
        "GET",
        "verify/entity/relationships",
        {"lei": a.get("lei")},
        None,
    ),
}
