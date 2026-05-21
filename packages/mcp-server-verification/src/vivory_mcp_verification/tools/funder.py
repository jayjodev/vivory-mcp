"""Crossref Funder Registry resolver.

Funding acknowledgments are a verification surface: claims like "funded by
NIH" can be cross-referenced against the canonical Funder Registry (used
to disambiguate ~130M Crossref records). Returns canonical Funder ID,
alt-names, country, work-count.

Source: api.crossref.org/funders, free, keyless.

Backed by /api/verify/funder.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="verify_funder",
        description=(
            "Resolve a funder name (or 10-digit Funder ID) to its canonical "
            "Crossref Funder Registry record. Returns the official name, "
            "alt-names, location/country, work-count, URI, and hierarchy. "
            "Use for: (a) verifying an AI-cited funder exists, (b) "
            "disambiguating between funder name variants (e.g. NIH vs "
            "National Institutes of Health), (c) cross-referencing "
            "acknowledgments against the canonical registry."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 2,
                    "description": "Funder name (e.g. 'NIH') or 10-digit Funder ID.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_funder": lambda a: (
        "GET",
        "verify/funder",
        {"query": a.get("query"), "limit": a.get("limit") or 10},
        None,
    ),
}
