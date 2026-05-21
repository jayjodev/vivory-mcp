"""Retraction status — single-DOI 3-source reconcile + corpus streams.

Three tools, two directions:

- `doi_retraction_status` — *single DOI* 3-source reconcile (Crossref
  crossmark + OpenAlex is_retracted + PubPeer post-pub commentary). Returns
  a Verified Fact corpus record (verdict + discrepancy + provenance hash)
  persisted with (doi, as_of) idempotency. Use before citing a paper in a
  brief, a literature review, or a RAG corpus.
- `retraction_watch_recent` — *reverse direction* — last N days of
  retraction events. Use to audit a corpus you already cited.
- `retraction_watch_by_journal` — retractions filtered to a single journal
  (ISSN or name). Use before publishing a set of citations from one venue.

Backed by /api/verify/doi/retraction-status + /api/verify/retraction/* on
api.vivory.app. Upstream = api.crossref.org + api.openalex.org +
pubpeer.com + Retraction Watch (Crossref-mirrored, public).
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="doi_retraction_status",
        description=(
            "Reconciled 3-source retraction status for a single DOI: "
            "Crossref crossmark (`update-to` with type retraction / "
            "withdrawal / expression_of_concern) × OpenAlex `is_retracted` "
            "× PubPeer post-publication commentary. Returns a Verified "
            "Fact corpus record — `verdict` (retracted / disputed / "
            "flagged_few_comments / clean / not_found), `discrepancy` "
            "(true when Crossref XOR OpenAlex disagree, or when no formal "
            "retraction exists yet but PubPeer is actively flagging the "
            "paper), a tamper-evident `provenance_hash`, and `as_of`. "
            "Persisted with (doi, as_of) idempotency so the same DOI on "
            "the same day reuses the record. Use this before citing a "
            "paper in a brief, a literature review, or ingesting it into "
            "a RAG corpus; single-source checks (crossmark only, OpenAlex "
            "only) routinely false-pass real retractions."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {
                    "type": "string",
                    "minLength": 4,
                    "maxLength": 200,
                    "description": (
                        "DOI of the paper to verify. With or without "
                        "`https://doi.org/` or `doi:` prefix."
                    ),
                },
            },
            "required": ["doi"],
            "additionalProperties": False,
        },
    ),
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
    "doi_retraction_status": lambda a: (
        "GET",
        "verify/doi/retraction-status",
        {"doi": a.get("doi")},
        None,
    ),
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
