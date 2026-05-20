"""ORCID author identity verification.

ORCID iDs are the canonical author identifier for academic work — every
modern publisher, preprint server, and funder uses them. Vivory wraps the
free ORCID public API into a single envelope so an LLM about to cite an
author can confirm: (a) the iD resolves to a real person, (b) the name
matches what the LLM is claiming, (c) the iD has actually published the
work being cited (chain via doi: from `orcid_works`).

Backed by /api/verify/orcid/* on api.vivory.app. No upstream key required;
ORCID public API has a generous public quota.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_ORCID = {
    "type": "string",
    "minLength": 16,
    "maxLength": 200,
    "description": (
        "ORCID iD in any common form — '0000-0002-1825-0097', "
        "'https://orcid.org/0000-0002-1825-0097', or bare 16 digits. "
        "Vivory normalizes."
    ),
}

TOOLS: list[Tool] = [
    Tool(
        name="verify_orcid",
        description=(
            "Resolve an ORCID iD to its public identity envelope: canonical "
            "iD, name (given + family), public emails, keywords, and a "
            "works_count summary. Use this as the **first** check on any "
            "author-attributed citation — if the iD does not resolve, the "
            "downstream cite is fabricated. Sources: orcid.org public API."
        ),
        inputSchema={
            "type": "object",
            "properties": {"orcid": _ORCID},
            "required": ["orcid"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="orcid_works",
        description=(
            "List the works (papers, datasets, preprints) registered to an "
            "ORCID iD. Returns title, year, type, and DOI when present. "
            "Chain the returned DOIs into `verify_doi` / `doi_retraction_check` "
            "to confirm a claimed paper actually belongs to this author and "
            "is not retracted. Default limit 20, max 100."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "orcid": _ORCID,
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
            },
            "required": ["orcid"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_orcid": lambda a: ("GET", "verify/orcid", {"orcid": a.get("orcid")}, None),
    "orcid_works": lambda a: (
        "GET",
        "verify/orcid/works",
        {"orcid": a.get("orcid"), "limit": a.get("limit")},
        None,
    ),
}
