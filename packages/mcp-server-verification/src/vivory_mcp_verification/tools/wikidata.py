"""Wikidata entity grounding tools.

Wikidata Q-numbers (e.g. Q42 = Douglas Adams) are canonical IDs that
survive label rewrites and ambiguity. The first-call grounding step
before an LLM cites any person / place / org / concept by name —
hallucination backbone for global entity verification.

Backed by /api/verify/wikidata + /api/verify/wikidata/search on
api.vivory.app. Vivory throttles upstream (Wikidata polite use).
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_QID = {
    "type": "string",
    "minLength": 2,
    "maxLength": 20,
    "pattern": "^[Qq][0-9]+$",
    "description": "Wikidata Q-number (e.g. Q42, Q937).",
}


TOOLS: list[Tool] = [
    Tool(
        name="verify_qid",
        description=(
            "Resolve a Wikidata Q-number to canonical record: label, "
            "description, aliases, Wikipedia URL, instance-of (P31), "
            "country (P17), and total claim count. Use as the default "
            "first call on any entity (person/place/org/concept) an LLM "
            "is about to cite — Q-numbers survive label drift."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "qid": _QID,
                "lang": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 8,
                    "default": "en",
                    "description": "Language code for label/description (en, ko, ja, …).",
                },
            },
            "required": ["qid"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="wikidata_search",
        description=(
            "Search Wikidata for entities matching free-text. Returns "
            "candidate Q-numbers with label + short description — pick "
            "one then call verify_qid for the full record. Use when the "
            "agent has an entity name but no Q-number."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {"type": "string", "minLength": 2, "maxLength": 200},
                "lang": {"type": "string", "minLength": 2, "maxLength": 8, "default": "en"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
            },
            "required": ["q"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_qid": lambda a: ("GET", "verify/wikidata", {"qid": a.get("qid"), "lang": a.get("lang")}, None),
    "wikidata_search": lambda a: (
        "GET",
        "verify/wikidata/search",
        {"q": a.get("q"), "lang": a.get("lang"), "limit": a.get("limit")},
        None,
    ),
}
