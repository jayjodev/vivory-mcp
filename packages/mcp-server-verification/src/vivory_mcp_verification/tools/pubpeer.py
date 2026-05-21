"""PubPeer post-publication peer-review status.

PubPeer is the de-facto anonymous post-publication peer review surface.
A paper can be live in its journal yet flagged here with image-manipulation,
statistical, ethical, or fraud concerns. Pre-citation screen.

Verdict scale: clear (0 comments) / flagged_few_comments (1-2) /
flagged_active_discussion (≥3). Counts only — content of comments is not
piped through the gateway.

Backed by /api/verify/peer-review/pubpeer. Requires PUBPEER_DEV_KEY env on
the backend; without it, returns a scaffold envelope with the canonical
public search link.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="verify_pubpeer_status",
        description=(
            "Check PubPeer for post-publication peer-review commentary on a "
            "DOI. PubPeer is the anonymous community-flagging surface for "
            "fraud / image manipulation / statistical / ethical concerns — "
            "papers can be alive in their journal yet flagged here. Returns "
            "verdict (clear / flagged_few_comments / flagged_active_"
            "discussion), comment_count, first/latest comment dates, and a "
            "canonical public search link."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {
                    "type": "string",
                    "minLength": 5,
                    "description": "Article DOI (with or without https://doi.org/ prefix).",
                },
            },
            "required": ["doi"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_pubpeer_status": lambda a: (
        "GET",
        "verify/peer-review/pubpeer",
        {"doi": a.get("doi")},
        None,
    ),
}
