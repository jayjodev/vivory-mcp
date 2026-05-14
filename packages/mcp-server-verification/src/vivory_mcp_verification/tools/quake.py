"""USGS Earthquake seismic-event verification tools.

USGS is the global authoritative primary source for seismic events
(≥M2.5 in the United States, ≥M4.5 worldwide). Vivory wraps the FDSN
event API into citation trail: event ID → canonical magnitude, place,
time, depth, tsunami flag.

Backed by /api/verify/quake + /api/verify/quake/recent.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="verify_quake",
        description=(
            "Resolve a USGS earthquake event ID to canonical record: "
            "magnitude, place description, UTC time, lat/lon, depth (km), "
            "tsunami flag, alert level, felt-reports count. Use before an "
            "LLM cites a specific earthquake — USGS event IDs look like "
            "'us7000kufc', 'ci39893640'."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "event_id": {
                    "type": "string",
                    "minLength": 6,
                    "maxLength": 40,
                    "description": "USGS event ID (e.g. 'us7000kufc').",
                },
            },
            "required": ["event_id"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="recent_quakes",
        description=(
            "Return recent earthquakes at or above `min_magnitude` in "
            "the last `hours` hours, ordered by time. Use for event-"
            "existence claims — 'there was a M6 quake in region X this "
            "week' — confirms the event was recorded by USGS."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "min_magnitude": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 10.0,
                    "default": 4.5,
                },
                "hours": {"type": "integer", "minimum": 1, "maximum": 720, "default": 24},
                "limit": {"type": "integer", "minimum": 1, "maximum": 200, "default": 20},
            },
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_quake": lambda a: ("GET", "verify/quake", {"event_id": a.get("event_id")}, None),
    "recent_quakes": lambda a: (
        "GET",
        "verify/quake/recent",
        {
            "min_magnitude": a.get("min_magnitude"),
            "hours": a.get("hours"),
            "limit": a.get("limit"),
        },
        None,
    ),
}
