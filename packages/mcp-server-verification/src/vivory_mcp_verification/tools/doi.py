"""DOI verification tools.

DOI (Digital Object Identifier) is the lingua franca of scholarly citation.
Vivory wraps Crossref + OpenAlex + RetractionWatch into a single
authoritative resolver: one DOI in, full provenance out — metadata, status,
retraction history, author network with ORCID linking.

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
        name="doi_metadata",
        description=(
            "Full metadata record for a DOI — Crossref + OpenAlex merged. "
            "Includes title, authors with ORCID, publication date, journal "
            "+ ISSN, publisher, type (journal-article / preprint / dataset / "
            "book-chapter), abstract when available, citation counts, "
            "references count, funder list. Heavier than verify_doi; use "
            "this when the agent actually needs to render a full citation."
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
    Tool(
        name="doi_author_network",
        description=(
            "Co-author network around a DOI's authors. For each author, "
            "returns ORCID, h-index, top-5 collaborators (from OpenAlex), "
            "most-cited paper, and any retraction history. Useful for "
            "vetting whether a citation comes from a recognized expert "
            "(actual academic) vs. an unknown name (possible LLM "
            "fabrication). Heavy call — caches 24h on the gateway."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doi": _DOI,
                "depth": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 2,
                    "default": 1,
                    "description": "1 = direct authors only; 2 = include first-degree co-authors.",
                },
            },
            "required": ["doi"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_doi": lambda a: ("GET", "verify/doi", {"doi": a.get("doi")}, None),
    "doi_metadata": lambda a: ("GET", "verify/doi/metadata", {"doi": a.get("doi")}, None),
    "doi_retraction_check": lambda a: ("GET", "verify/doi/retraction", {"doi": a.get("doi")}, None),
    "doi_author_network": lambda a: (
        "GET",
        "verify/doi/authors",
        {"doi": a.get("doi"), "depth": a.get("depth")},
        None,
    ),
}
