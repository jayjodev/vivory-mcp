"""Wikipedia external-citation health audit.

Even a live, well-maintained Wikipedia article can rest on a citation
backbone full of 404s, domain-parked pages, or paywalled links. This tool
samples the article's external links, HEAD-checks them, and reports % live
+ a status histogram + the dead-or-failing list.

Source: <lang>.wikipedia.org/w/api.php (extlinks), free, keyless.

Backed by /api/verify/wikipedia/cite-health.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="verify_wikipedia_cite_health",
        description=(
            "Audit the external references of a Wikipedia article for "
            "liveness. Given a full Wikipedia article URL, pulls its external "
            "links, HEAD-checks a sample, and returns verdict (healthy / "
            "frayed / decaying / no_external_links), live_ratio, status "
            "buckets (ok / client_4xx / server_5xx / network_error), and the "
            "dead-or-failing list. Use when an AI grounds a claim on a "
            "Wikipedia article — verify its citation backbone isn't rotting."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Full Wikipedia article URL (https://<lang>.wikipedia.org/wiki/<Title>).",
                },
                "sample": {
                    "type": "integer",
                    "minimum": 5,
                    "maximum": 50,
                    "default": 20,
                    "description": "How many external links to HEAD-check (round-robin by host).",
                },
            },
            "required": ["url"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_wikipedia_cite_health": lambda a: (
        "GET",
        "verify/wikipedia/cite-health",
        {"url": a.get("url"), "sample": a.get("sample") or 20},
        None,
    ),
}
