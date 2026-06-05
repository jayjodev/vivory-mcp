"""DOI verification tools.

DOI (Digital Object Identifier) is the lingua franca of scholarly citation.
Vivory wraps Crossref + OpenAlex + RetractionWatch into an authoritative
resolver: one DOI in, a verdict + retraction status out — the two primitives
an LLM needs *before* it cites a paper.

Trimmed to the moat in v0.14.0 (2026-06-05): doi_metadata + doi_author_network
retired with the commodity-tool cut. verify_doi (verdict) + doi_retraction_check
(retraction gate) stay as the research-integrity anchor.

Backed by /api/verify/doi/* on api.vivory.app. Free tier 500 lookups/day,
Pro 10,000/day. All upstream attribution preserved (Crossref / OpenAlex
remain the canonical record; Vivory only normalizes).
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_DOI = {
    "type": "string",
    "minLength": 4,
    "maxLength": 200,
    "description": (
        "DOI in any common form — '10.1234/foo.bar', "
        "'https://doi.org/10.1234/foo.bar', or the bare '10.1234/foo.bar'. "
        "Vivory normalizes."
    ),
}

TOOLS: list[Tool] = [
    Tool(
        name="verify_doi",
        description=(
            "Resolve a DOI and return a single verdict envelope: status "
            "(active / retracted / withdrawn / not-found), canonical metadata "
            "(title, authors, year, journal, publisher), open-access state, "
            "and the upstream sources that contributed (Crossref + OpenAlex "
            "+ RetractionWatch). Use this as the default first call on any "
            "DOI an LLM is about to cite."
        ),
        inputSchema={
            "type": "object",
            "properties": {"doi": _DOI},
            "required": ["doi"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="doi_retraction_check",
        description=(
            "Check whether a DOI has been retracted, withdrawn, expressed-"
            "concern, or corrected. Returns the retraction notice DOI when "
            "available, the date, the reason category (data-fabrication / "
            "image-manipulation / authorship-dispute / publisher-error / "
            "etc.), and a short verbatim quote from the notice. Sourced from "
            "RetractionWatch + Crossref crossmark. **Critical** before an "
            "LLM cites any paper as supporting evidence."
        ),
        inputSchema={
            "type": "object",
            "properties": {"doi": _DOI},
            "required": ["doi"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_doi": lambda a: ("GET", "verify/doi", {"doi": a.get("doi")}, None),
    "doi_retraction_check": lambda a: ("GET", "verify/doi/retraction", {"doi": a.get("doi")}, None),
}
