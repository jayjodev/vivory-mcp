"""OpenCitations COCI — DOI citation context.

The free OSS alternative to Scite.ai citation context. For a given DOI,
returns the list of citing or referenced DOIs with timespan + same-journal
+ same-author flags. Useful for citation cartel detection, self-citation
ratio audit, and citation graph traversal.

Source: opencitations.net/index/coci/api/v1, free, keyless. Updated weekly
from Crossref + DataCite.

Backed by /api/verify/doi/citations.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="verify_doi_citations",
        description=(
            "Fetch citation context for a DOI via OpenCitations COCI. Returns "
            "either citing papers (direction='citing', default) or references "
            "this paper makes (direction='references'). Each row includes the "
            "OCI identifier, citing/cited DOIs, creation date, timespan, "
            "journal_sc (same-journal flag), and author_sc (self-citation "
            "flag). Surfaces self-citation count as a quick signal."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {
                    "type": "string",
                    "minLength": 5,
                    "description": "DOI of the article whose citation context to fetch.",
                },
                "direction": {
                    "type": "string",
                    "enum": ["citing", "references"],
                    "default": "citing",
                    "description": "citing = who cites this paper; references = which DOIs this paper cites.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20,
                },
            },
            "required": ["doi"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_doi_citations": lambda a: (
        "GET",
        "verify/doi/citations",
        {
            "doi": a.get("doi"),
            "direction": a.get("direction") or "citing",
            "limit": a.get("limit") or 20,
        },
        None,
    ),
}
