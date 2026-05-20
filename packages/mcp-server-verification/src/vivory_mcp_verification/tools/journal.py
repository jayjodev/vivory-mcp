"""Predatory + low-quality journal detection.

Citation hallucinations + paper-mill output often land on predatory
journals that publish without genuine peer review. This tool wraps the
DOAJ (Directory of Open Access Journals) whitelist + a small heuristic
panel so a citation's journal can be sanity-checked before quoting.

Verdict scale: trusted (DOAJ-listed + no flags) / unknown (not in DOAJ
but no flags) / suspicious (one or more heuristic flags) / known_predatory
(matched against the curated predatory list distilled from Beall's list +
its successors).

Heuristic flags include: fake impact-factor claim, ISSN structurally
invalid, suspicious publisher pattern, ridiculous claimed peer-review
turnaround (<7 days).

Backed by /api/verify/journal/quality. DOAJ public API, no key required.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="verify_journal_quality",
        description=(
            "Verify a journal's quality / trust level. Input is the journal "
            "name or its ISSN. Returns a verdict (trusted / unknown / "
            "suspicious / known_predatory), DOAJ membership status, ISSN "
            "structural validity, and a list of heuristic flags. Use this "
            "before quoting any citation — if verdict is suspicious or "
            "known_predatory, the cited claim should not be propagated "
            "without an independent source. Source: DOAJ public API + "
            "Vivory curated predatory list."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "journal": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 300,
                    "description": (
                        "Journal name ('Nature Communications') or ISSN "
                        "('2041-1723' / '20411723')."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 5,
                    "description": (
                        "Max DOAJ name-match candidates to return when query "
                        "is ambiguous."
                    ),
                },
            },
            "required": ["journal"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_journal_quality": lambda a: (
        "GET",
        "verify/journal/quality",
        {"journal": a.get("journal"), "limit": a.get("limit") or 5},
        None,
    ),
}
