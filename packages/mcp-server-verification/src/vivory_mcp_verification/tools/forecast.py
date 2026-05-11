"""Forecast track-record + agent submission tools.

Vivory's forecast pipeline (originally Intel weekly, Phase 3 Forecast Verify
MCP candidate) keeps a public track record: every forecast registered, the
deadline, the verdict at close, the Brier score. Agents that want to
make claims about a forecaster's accuracy — including their own — can
look up the record. Agents that want to register a new forecast for
later auto-verification can submit one.

Note: forecast submission is a registration, not a binding contract.
Vivory verifies and tracks; legal exposure for the forecast itself stays
with the submitting agent.

Backed by /api/verify/forecast/* on api.vivory.app.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="forecast_track_record",
        description=(
            "Look up the closed-forecast track record. Returns total "
            "forecasts, verdict counts (correct / partial / wrong / "
            "unresolved), Brier score (lower = better calibration; <0.25 "
            "good, <0.20 great), and the latest 20 closed forecasts. "
            "Filter by forecaster_id (specific agent or human), scope "
            "(crypto / korea / general), or since (ISO date)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "forecaster_id": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 200,
                    "description": "Specific forecaster — human handle or agent ID. Omit for global track record.",
                },
                "scope": {
                    "type": "string",
                    "enum": ["crypto", "korea", "general", "all"],
                    "default": "all",
                },
                "since": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "ISO date YYYY-MM-DD; only include forecasts closed on or after this date.",
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 200, "default": 20},
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="submit_forecast",
        description=(
            "Register a forecast for later auto-verification. The agent "
            "submits a claim, deadline, and supporting evidence URLs. "
            "Vivory closes the forecast at the deadline (or earlier if "
            "the verdict becomes obvious), assigns correct / partial / "
            "wrong, and updates the forecaster's Brier score. The "
            "submission returns a forecast_id which the agent can publish "
            "alongside its claim — anyone can later verify with "
            "forecast_track_record. Submission is free; verification is "
            "free. Legal exposure for the forecast content stays with "
            "the submitter."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "claim": {
                    "type": "string",
                    "minLength": 10,
                    "maxLength": 1000,
                    "description": "The forecast in plain language. Should be falsifiable.",
                },
                "deadline": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}(T\\d{2}:\\d{2}(:\\d{2})?(Z|[+-]\\d{2}:?\\d{2})?)?$",
                    "description": "ISO date or datetime when the forecast resolves.",
                },
                "scope": {
                    "type": "string",
                    "enum": ["crypto", "korea", "general"],
                    "default": "general",
                },
                "evidence_urls": {
                    "type": "array",
                    "items": {"type": "string", "format": "uri"},
                    "maxItems": 20,
                    "description": "Supporting URLs the forecaster considered. Will be Wayback-snapshotted on submit.",
                },
                "forecaster_id": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 200,
                    "description": (
                        "Stable identifier for the forecaster — used to "
                        "compute the per-forecaster Brier score. Free-text; "
                        "agents typically use their public handle."
                    ),
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Subjective probability the forecast resolves correct (0-1). Used for Brier scoring.",
                },
            },
            "required": ["claim", "deadline", "forecaster_id"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "forecast_track_record": lambda a: (
        "GET",
        "verify/forecast/track-record",
        {
            "forecaster_id": a.get("forecaster_id"),
            "scope": a.get("scope"),
            "since": a.get("since"),
            "limit": a.get("limit"),
        },
        None,
    ),
    "submit_forecast": lambda a: (
        "POST",
        "verify/forecast/submit",
        None,
        {
            "claim": a.get("claim"),
            "deadline": a.get("deadline"),
            "scope": a.get("scope") or "general",
            "evidence_urls": a.get("evidence_urls") or [],
            "forecaster_id": a.get("forecaster_id"),
            "confidence": a.get("confidence"),
        },
    ),
}
