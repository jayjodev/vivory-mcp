"""Korea Tourism Organization (KTO) — TourAPI tools.

Backed by /api/public-tools/tour/* on api.vivory.app.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_LANG = {
    "type": "string",
    "enum": ["ko", "en"],
    "default": "ko",
    "description": "Language. `en` falls back to Korean when missing.",
}
_AREA_CODE = {
    "type": "string",
    "description": "TourAPI area code: 1=Seoul, 2=Incheon, 3=Daejeon, 4=Daegu, 5=Gwangju, 6=Busan, 7=Ulsan, 8=Sejong, 31=Gyeonggi, 32=Gangwon, 33=Chungbuk, 34=Chungnam, 35=Gyeongbuk, 36=Gyeongnam, 37=Jeonbuk, 38=Jeonnam, 39=Jeju.",
}

TOOLS: list[Tool] = [
    Tool(
        name="kto_tour_list",
        description=(
            "Korea Tourism Organization curated tour spots by region. Returns "
            "title, address, content_id (use kto_tour_detail for full record)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "area_code": _AREA_CODE,
                "lang": _LANG,
                "num_rows": {"type": "integer", "minimum": 1, "maximum": 100, "default": 30},
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kto_festival_search",
        description=(
            "Festivals and events active within a date range. Useful when an AI "
            "agent plans a Korea trip — pick festivals overlapping the user's "
            "travel window. event_start_date is required (YYYYMMDD)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "event_start_date": {
                    "type": "string",
                    "pattern": "^\\d{8}$",
                    "description": "YYYYMMDD (required).",
                },
                "event_end_date": {
                    "type": "string",
                    "pattern": "^\\d{8}$",
                    "description": "YYYYMMDD (optional, default = end of next month).",
                },
                "area_code": _AREA_CODE,
                "lang": _LANG,
                "num_rows": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
            },
            "required": ["event_start_date"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kto_tour_nearby",
        description=(
            "Tour spots within a radius of a coordinate (WGS84). Default radius "
            "1 km, max 20 km. Useful for itinerary expansion (\"what else is "
            "near where I already am?\")."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "lat": {"type": "number", "minimum": 33, "maximum": 39},
                "lng": {"type": "number", "minimum": 124, "maximum": 132},
                "radius": {
                    "type": "number",
                    "minimum": 100,
                    "maximum": 20000,
                    "default": 1000,
                    "description": "Search radius in meters (100~20000).",
                },
            },
            "required": ["lat", "lng"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kto_tour_detail",
        description=(
            "Full detail record for a tour spot by content_id (from kto_tour_list "
            "or kto_tour_nearby). Auto-falls-back to Korean when an English "
            "translation is missing."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "content_id": {
                    "type": "string",
                    "description": "TourAPI contentId (numeric string).",
                },
                "lang": _LANG,
            },
            "required": ["content_id"],
            "additionalProperties": False,
        },
    ),
]


def _h(path_template: str, builder: Callable[[dict], dict] = lambda a: {}) -> Callable[[dict], tuple[str, dict]]:
    def handler(args: dict) -> tuple[str, dict]:
        return path_template.format(**args), builder(args)
    return handler


HANDLERS: dict[str, Callable[[dict], tuple[str, dict]]] = {
    "kto_tour_list": _h(
        "tour/list",
        lambda a: {
            "area_code": a.get("area_code"),
            "lang": a.get("lang"),
            "num_rows": a.get("num_rows"),
        },
    ),
    "kto_festival_search": _h(
        "tour/festival",
        lambda a: {
            "event_start_date": a.get("event_start_date"),
            "event_end_date": a.get("event_end_date"),
            "area_code": a.get("area_code"),
            "lang": a.get("lang"),
            "num_rows": a.get("num_rows"),
        },
    ),
    "kto_tour_nearby": _h(
        "tour/near",
        lambda a: {
            "lat": a.get("lat"),
            "lng": a.get("lng"),
            "radius": a.get("radius"),
        },
    ),
    "kto_tour_detail": _h(
        "tour/detail/{content_id}",
        lambda a: {"lang": a.get("lang")},
    ),
}
