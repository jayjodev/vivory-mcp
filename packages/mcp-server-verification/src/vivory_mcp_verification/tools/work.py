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
    Tool(
        name="verify_salami_slicing",
        description=(
            "Screen an author's bibliography for salami-slicing — publishing "
            "near-duplicate work as separate papers. Pulls the author's "
            "OpenAlex works, computes a token-Jaccard similarity matrix over "
            "(title + abstract), and flags pairs ≥ threshold. Returns verdict "
            "(clear / moderate_overlap_screen / high_overlap_screen) + flagged "
            "pairs. NOTE: false positives are expected for series papers / "
            "longitudinal studies — verdict is 'screen', not 'guilty'. Input "
            "is an OpenAlex author ID (A…) or an ORCID."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "author_id": {
                    "type": "string",
                    "description": "OpenAlex author ID (A…) or ORCID (0000-0000-0000-0000).",
                },
                "threshold": {
                    "type": "number",
                    "minimum": 0.3,
                    "maximum": 0.95,
                    "default": 0.55,
                    "description": "Min Jaccard similarity to flag a pair.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 5,
                    "maximum": 50,
                    "default": 25,
                    "description": "Max recent works to pull and compare.",
                },
            },
            "required": ["author_id"],
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
    "verify_salami_slicing": lambda a: (
        "GET",
        "verify/work/salami",
        {
            "author_id": a.get("author_id"),
            "threshold": a.get("threshold") or 0.55,
            "limit": a.get("limit") or 25,
        },
        None,
    ),
}
