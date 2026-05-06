"""Opinet (한국석유공사) gas-price tools.

Backed by /api/public-tools/opinet/* on api.vivory.app.
Shared 1,500-call/day quota across all Vivory consumers — backend handles
quota tracking and returns 429 when exhausted.

Fuel codes: B027 = regular gasoline (보통휘발유), B034 = premium gasoline
(고급휘발유), D047 = diesel (경유), K015 = kerosene (등유), C004 = LPG.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_PRODCD = {
    "type": "string",
    "enum": ["B027", "B034", "D047", "K015", "C004"],
    "description": "B027 gasoline / B034 premium gasoline / D047 diesel / K015 kerosene / C004 LPG.",
}

TOOLS: list[Tool] = [
    Tool(
        name="opinet_national_avg",
        description=(
            "Korea nationwide gas-price average across all 5 fuel grades "
            "(gasoline / premium / diesel / kerosene / LPG). 1-hour backend cache. "
            "Source: Opinet (한국석유공사)."
        ),
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    Tool(
        name="opinet_sido_avg",
        description=(
            "Korea per-SIDO (province) gas-price average for one fuel grade. "
            "Returns 17 SIDOs ranked by price. Default fuel = regular gasoline (B027)."
        ),
        inputSchema={
            "type": "object",
            "properties": {"prodcd": _PRODCD},
            "additionalProperties": False,
        },
    ),
    Tool(
        name="opinet_lowest_top10",
        description=(
            "Top 10 cheapest gas stations for a fuel grade — nationwide or within "
            "an Opinet SIDO area code. Useful for travel planning. Default fuel = B027."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "prodcd": _PRODCD,
                "area": {
                    "type": "string",
                    "pattern": "^\\d{2}$",
                    "description": "Opinet SIDO 2-digit code (01~19). Omit for nationwide.",
                },
            },
            "additionalProperties": False,
        },
    ),
]


def _h(path: str, builder: Callable[[dict], dict] = lambda a: {}) -> Callable[[dict], tuple[str, dict]]:
    def handler(args: dict) -> tuple[str, dict]:
        return path, builder(args)
    return handler


HANDLERS: dict[str, Callable[[dict], tuple[str, dict]]] = {
    "opinet_national_avg": _h("opinet/national-avg"),
    "opinet_sido_avg": _h("opinet/sido-avg", lambda a: {"prodcd": a.get("prodcd")}),
    "opinet_lowest_top10": _h(
        "opinet/lowest",
        lambda a: {"prodcd": a.get("prodcd"), "area": a.get("area")},
    ),
}
