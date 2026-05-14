"""USPTO PatentsView US patent verification tools.

US patent numbers are canonical identifiers issued by the United States
Patent and Trademark Office. PatentsView is the USPTO-hosted research
API over the same data. Sister of KIPRIS (Korean patents on Korea MCP).

Backed by /api/verify/patent + /api/verify/patent/search on api.vivory.app.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="verify_patent",
        description=(
            "Resolve a US patent number to canonical record: title, "
            "abstract, grant date, inventors, assignees (corporate "
            "owner), claim count. Use before an LLM cites a US patent — "
            "confirms it exists at USPTO and surfaces the assignee."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "patent_number": {
                    "type": "string",
                    "minLength": 4,
                    "maxLength": 20,
                    "description": "US patent number (e.g. '10000000', commas allowed).",
                },
            },
            "required": ["patent_number"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="patent_search",
        description=(
            "Search USPTO PatentsView by free-text query over title + "
            "abstract, optionally filtered by assignee org name + grant "
            "year. Returns up to `limit` patents — pick one then call "
            "verify_patent."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {"type": "string", "minLength": 2, "maxLength": 300},
                "assignee": {"type": "string", "maxLength": 200, "description": "Assignee organization name filter."},
                "year": {"type": "integer", "minimum": 1976, "maximum": 2030, "description": "Grant year filter."},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
            },
            "required": ["q"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_patent": lambda a: (
        "GET",
        "verify/patent",
        {"patent_number": a.get("patent_number")},
        None,
    ),
    "patent_search": lambda a: (
        "GET",
        "verify/patent/search",
        {"q": a.get("q"), "assignee": a.get("assignee"), "year": a.get("year"), "limit": a.get("limit")},
        None,
    ),
}
