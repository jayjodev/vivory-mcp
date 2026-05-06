"""KMA (Korea Meteorological Administration) weather tools.

Backed by /api/public-tools/weather/* on api.vivory.app.
KMA license — citation required, returned in response attribution.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="kma_weather_current",
        description=(
            "Korea Meteorological Administration ultra-short-term observation "
            "(present-time temperature, humidity, wind, precipitation). Provide "
            "either `city` preset (Seoul / Busan / etc.) or `lat`+`lng` "
            "(WGS84 — auto-converted to KMA grid). 10-minute backend cache."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City preset name (e.g. Seoul, 부산)."},
                "lat": {"type": "number", "minimum": 33, "maximum": 39},
                "lng": {"type": "number", "minimum": 124, "maximum": 132},
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kma_weather_forecast",
        description=(
            "KMA short-range forecast — village forecast (3-day, default) or "
            "ultra-short forecast (6-hour). Provide `city` preset OR `lat`+`lng`. "
            "Returns hourly TMP/REH/WSD/POP series."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "lat": {"type": "number", "minimum": 33, "maximum": 39},
                "lng": {"type": "number", "minimum": 124, "maximum": 132},
                "range": {"type": "string", "enum": ["village", "short"], "default": "village"},
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kma_weather_cities",
        description=(
            "List supported KMA city presets (the candidates for the `city` "
            "parameter on kma_weather_current / kma_weather_forecast). Includes "
            "Korean and English names plus KMA grid coordinates."
        ),
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
]


def _h(path: str, builder: Callable[[dict], dict] = lambda a: {}) -> Callable[[dict], tuple[str, dict]]:
    def handler(args: dict) -> tuple[str, dict]:
        return path, builder(args)
    return handler


HANDLERS: dict[str, Callable[[dict], tuple[str, dict]]] = {
    "kma_weather_current": _h(
        "weather/current",
        lambda a: {"city": a.get("city"), "lat": a.get("lat"), "lng": a.get("lng")},
    ),
    "kma_weather_forecast": _h(
        "weather/forecast",
        lambda a: {
            "city": a.get("city"),
            "lat": a.get("lat"),
            "lng": a.get("lng"),
            "range": a.get("range"),
        },
    ),
    "kma_weather_cities": _h("weather/cities"),
}
