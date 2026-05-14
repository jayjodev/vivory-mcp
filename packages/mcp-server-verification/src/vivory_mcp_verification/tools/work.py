"""OpenAlex academic work tools — sister of the DOI cluster.

Where the DOI cluster is Crossref-first (publisher record), the work
cluster is OpenAlex-first (citation graph). Use when the agent has an
OpenAlex W-ID or wants free-text paper search with citation counts and
open-access URLs surfaced.

Backed by /api/verify/work + /api/verify/work/search on api.vivory.app.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="verify_work",
        description=(
            "Resolve an OpenAlex work ID (e.g. W2741809807) or DOI to the "
            "canonical academic record: title, year, type, authors with "
            "ORCIDs and institutions, open-access status + URL, citation "
            "count, retraction flag, primary topic. Use as the citation-graph "
            "first call when an LLM is about to cite a paper."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "id": {"type": "string", "maxLength": 200, "description": "OpenAlex work ID (W…) or full URL."},
                "doi": {"type": "string", "maxLength": 200, "description": "DOI alternative to id (10.…)."},
            },
            "anyOf": [{"required": ["id"]}, {"required": ["doi"]}],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="search_works",
        description=(
            "Free-text search OpenAlex works by topic / title. Returns up "
            "to `limit` candidate works with (W-ID, DOI, title, year, "
            "citation count, OA URL). Use when the agent has a paper name "
            "or topic but no DOI — pick the matching candidate, then call "
            "verify_work for the full record."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {"type": "string", "minLength": 2, "maxLength": 300},
                "year": {"type": "integer", "minimum": 1900, "maximum": 2100},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
            },
            "required": ["q"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_work": lambda a: ("GET", "verify/work", {"id": a.get("id"), "doi": a.get("doi")}, None),
    "search_works": lambda a: (
        "GET",
        "verify/work/search",
        {"q": a.get("q"), "year": a.get("year"), "limit": a.get("limit")},
        None,
    ),
}
