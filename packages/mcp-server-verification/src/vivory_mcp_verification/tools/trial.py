"""ClinicalTrials.gov v2 medical trial verification tools.

NCT (National Clinical Trial) IDs are the canonical registry for human-
subject medical trials worldwide. Vivory wraps ClinicalTrials.gov v2
into a verification surface — NCT in, canonical title + phase + status
+ sponsor + conditions + interventions + locations out.

Mission anchor: medical hallucination cost is the highest in the
verification cluster — wrong drug names, fabricated trial IDs, or
mis-attributed sponsors can carry real-life consequences. ClinicalTrials.gov
is the WHO ICMJE-mandated primary registry.

Backed by /api/verify/trial + /api/verify/trial/search on api.vivory.app.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_NCT = {
    "type": "string",
    "minLength": 4,
    "maxLength": 20,
    "pattern": "^[Nn][Cc][Tt][0-9]+$",
    "description": "ClinicalTrials.gov NCT identifier (e.g. NCT04368728).",
}


TOOLS: list[Tool] = [
    Tool(
        name="verify_trial",
        description=(
            "Resolve a clinical trial NCT identifier to the canonical "
            "ClinicalTrials.gov v2 record: brief + official title, phase, "
            "overall status (RECRUITING / COMPLETED / TERMINATED / …), "
            "study type, lead sponsor, conditions, interventions, start "
            "+ completion dates, location count. Use before an LLM cites "
            "a clinical trial — confirms the NCT exists and surfaces its "
            "current recruitment state."
        ),
        inputSchema={
            "type": "object",
            "properties": {"nct_id": _NCT},
            "required": ["nct_id"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="trial_search",
        description=(
            "Search ClinicalTrials.gov v2 by condition / intervention / "
            "sponsor / overall status. Returns up to `limit` NCT IDs with "
            "brief titles — pick one then call verify_trial. Use when the "
            "agent has a disease name or drug name but no NCT."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "condition": {"type": "string", "maxLength": 200, "description": "Disease / condition (e.g. 'glioblastoma')."},
                "intervention": {"type": "string", "maxLength": 200, "description": "Drug / device / procedure (e.g. 'pembrolizumab')."},
                "sponsor": {"type": "string", "maxLength": 200, "description": "Lead sponsor org name."},
                "status": {
                    "type": "string",
                    "maxLength": 50,
                    "description": "Overall status filter — e.g. RECRUITING, COMPLETED, TERMINATED, NOT_YET_RECRUITING.",
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
            },
            "anyOf": [
                {"required": ["condition"]},
                {"required": ["intervention"]},
                {"required": ["sponsor"]},
            ],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_trial": lambda a: ("GET", "verify/trial", {"nct_id": a.get("nct_id")}, None),
    "trial_search": lambda a: (
        "GET",
        "verify/trial/search",
        {
            "condition": a.get("condition"),
            "intervention": a.get("intervention"),
            "sponsor": a.get("sponsor"),
            "status": a.get("status"),
            "limit": a.get("limit"),
        },
        None,
    ),
}
