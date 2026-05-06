"""Mobility tools — EV chargers (환경부) + Seoul public parking + Seoul Bike (따릉이).

Backed by /api/public-tools/{ev-charge,parking,bike}/* on api.vivory.app.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="ev_chargers_by_region",
        description=(
            "Korean EV chargers within a SIDO with real-time status (occupied / "
            "available / out-of-service). Source: 환경부 한국전력 EV charger "
            "open API. SIDO admin codes (zcode 2-digit): 11=Seoul, 21=Busan, "
            "22=Daegu, 23=Incheon, 24=Gwangju, 25=Daejeon, 26=Ulsan, 29=Sejong, "
            "31=Gyeonggi, 32=Gangwon, 33=Chungbuk, 34=Chungnam, 35=Jeonbuk, "
            "36=Jeonnam, 37=Gyeongbuk, 38=Gyeongnam, 39=Jeju."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "zcode": {
                    "type": "string",
                    "pattern": "^\\d{2}$",
                    "description": "SIDO admin 2-digit code.",
                },
                "period": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 5,
                    "description": "Status refresh window in minutes (1~10).",
                },
            },
            "required": ["zcode"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="seoul_public_parking",
        description=(
            "Every Seoul-operated public parking lot (~2,300) with realtime "
            "availability merged in (~120 lots report live). Includes by-district "
            "stats. Optional Kakao Local geocoding (slow on first call, cached "
            "afterwards)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "geocode": {
                    "type": "boolean",
                    "default": True,
                    "description": "Fill lat/lng via Kakao Local. Default true.",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="seoul_bike_share",
        description=(
            "Every Seoul Bike (따릉이) station with real-time bike count. Includes "
            "by-district and status-tone (full / available / empty) statistics. "
            "Useful for last-mile travel planning."
        ),
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
]


def _h(path: str, builder: Callable[[dict], dict] = lambda a: {}) -> Callable[[dict], tuple[str, dict]]:
    def handler(args: dict) -> tuple[str, dict]:
        return path, builder(args)
    return handler


HANDLERS: dict[str, Callable[[dict], tuple[str, dict]]] = {
    "ev_chargers_by_region": _h(
        "ev-charge/region",
        lambda a: {"zcode": a.get("zcode"), "period": a.get("period")},
    ),
    "seoul_public_parking": _h(
        "parking/seoul",
        lambda a: {"geocode": a.get("geocode")},
    ),
    "seoul_bike_share": _h("bike/seoul"),
}
