"""Retraction Watch poller — recent retractions stream.

`verify_doi` already returns a single DOI's retraction status (via Crossref
crossmark + OpenAlex). This cluster adds the *reverse direction*: "what was
retracted recently?" — useful for agents auditing a corpus or watching a
journal.

- `retraction_watch_recent` — last N days of retraction events, optionally
  filtered by reason category (data-fabrication / image-manipulation /
  authorship-dispute / publisher-error / honest-error).
- `retraction_watch_by_journal` — retractions for a specific journal (ISSN
  or name), useful when an agent is about to cite multiple papers from the
  same venue.

Backed by /api/verify/retraction/* on api.vivory.app. Upstream =
Retraction Watch database (Crossref-mirrored, public).
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="retraction_watch_recent",
        description=(
            "Stream the most recent retraction notices (default last 30 days, "
            "max 365). For each notice: original DOI, retraction-notice DOI, "
            "retraction date, journal, publisher, reason category, short "
            "verbatim quote from the notice. Use this to sweep a freshly-"
            "cited corpus — feed each `original_doi` back into `verify_doi` "
            "to discover whether anything an agent already cited got "
            "retracted out from under it. Page with `offset`."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 365,
                    "default": 30,
                    "description": "Lookback window in days.",
                },
                "reason": {
                    "type": "string",
                    "maxLength": 64,
                    "description": (
                        "Optional reason filter. Common values: "
                        "data-fabrication, image-manipulation, authorship-"
                        "dispute, publisher-error, honest-error, plagiarism. "
                        "Partial match (ILIKE)."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 25,
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="retraction_watch_by_journal",
        description=(
            "List retractions for a single journal, by ISSN or name. Returns "
            "the same per-notice envelope as `retraction_watch_recent` plus "
            "the journal's lifetime retraction count and a recent-trend "
            "indicator (last-12-month count vs prior-12-month). Use before "
            "publishing a set of citations from a single venue."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "issn": {
                    "type": "string",
                    "pattern": r"^[0-9]{4}-[0-9]{3}[0-9X]$",
                    "description": "ISSN (e.g. '1476-4687' for Nature).",
                },
                "journal": {
                    "type": "string",
                    "maxLength": 200,
                    "description": (
                        "Journal name (partial match, ILIKE). Required if "
                        "`issn` is omitted."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 25,
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                },
            },
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "retraction_watch_recent": lambda a: (
        "GET",
        "verify/retraction/recent",
        {
            "days": a.get("days"),
            "reason": a.get("reason"),
            "limit": a.get("limit"),
            "offset": a.get("offset"),
        },
        None,
    ),
    "retraction_watch_by_journal": lambda a: (
        "GET",
        "verify/retraction/by-journal",
        {
            "issn": a.get("issn"),
            "journal": a.get("journal"),
            "limit": a.get("limit"),
            "offset": a.get("offset"),
        },
        None,
    ),
}
