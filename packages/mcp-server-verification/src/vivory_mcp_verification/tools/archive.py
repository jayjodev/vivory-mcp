"""Web archive lookup + capture tools.

Wraps the Wayback Machine + archive.today + Vivory's own snapshot cache
into a uniform lookup. Use cases:

- Before citing a URL: confirm it has a Wayback snapshot (verify_archive)
- Lock in evidence before it rots: trigger a fresh snapshot (wayback_capture)
- Show the URL's snapshot history: list all known captures (wayback_history)

Backed by /api/verify/archive/* + /api/archive/* on api.vivory.app.
Vivory deduplicates: capture-on-write rate is ~1 snapshot per URL per hour
(returns cached if hotter).
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_URL = {
    "type": "string",
    "format": "uri",
    "minLength": 8,
    "maxLength": 2000,
    "description": "The page URL to archive — http(s) only.",
}

TOOLS: list[Tool] = [
    Tool(
        name="verify_archive",
        description=(
            "Check whether a URL has Wayback Machine + archive.today coverage. "
            "Returns latest_snapshot_url, latest_snapshot_at, snapshot_count, "
            "and per-archive provider breakdown. Use as a pre-flight check "
            "before citing any web URL — if the answer is 'no archive yet', "
            "follow up with wayback_capture."
        ),
        inputSchema={
            "type": "object",
            "properties": {"url": _URL},
            "required": ["url"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="wayback_capture",
        description=(
            "Submit a URL to the Wayback Machine 'Save Page Now' API and "
            "return the resulting snapshot URL. Wayback rate-limits this "
            "to ~15/min globally; Vivory enforces a 1h cool-down per URL "
            "(returns the cached recent snapshot rather than a duplicate "
            "capture). Returns 202 + job_id for async captures."
        ),
        inputSchema={
            "type": "object",
            "properties": {"url": _URL},
            "required": ["url"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="wayback_history",
        description=(
            "Return the full list of Wayback snapshots for a URL — date, "
            "snapshot URL, status code at capture time. Useful for "
            "showing how a page changed over time, or finding the snapshot "
            "closest to a specific date when a claim was made. Default "
            "limit 50, max 500."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "url": _URL,
                "limit": {"type": "integer", "minimum": 1, "maximum": 500, "default": 50},
                "since": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "ISO date YYYY-MM-DD; only return snapshots on or after this date.",
                },
            },
            "required": ["url"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_archive": lambda a: ("GET", "verify/archive/check", {"url": a.get("url")}, None),
    "wayback_capture": lambda a: ("POST", "verify/archive/capture", None, {"url": a.get("url")}),
    "wayback_history": lambda a: (
        "GET",
        "verify/archive/history",
        {
            "url": a.get("url"),
            "limit": a.get("limit"),
            "since": a.get("since"),
        },
        None,
    ),
}
