"""Healthcare tools — HIRA (건강보험심사평가원) + NMC (국립중앙의료원 E-gen).

Backed by /api/public-tools/healthcare/* on api.vivory.app.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_NUM_ROWS = {"type": "integer", "minimum": 1, "maximum": 200, "default": 30}
_LAT = {"type": "number", "minimum": 33, "maximum": 39}
_LNG = {"type": "number", "minimum": 124, "maximum": 132}

TOOLS: list[Tool] = [
    Tool(
        name="hira_hospital_search",
        description=(
            "HIRA hospital directory search — every Korean hospital. Filter by "
            "SIDO code, name partial match, or both. 6-hour backend cache. "
            "Common SIDO codes: 110000=Seoul, 230000=Incheon, 260000=Daejeon, "
            "270000=Daegu, 280000=Ulsan, 290000=Gwangju, 310000=Busan, 360000=Sejong, "
            "410000=Gyeonggi, 420000=Gangwon, 430000=Chungbuk, 440000=Chungnam, "
            "450000=Jeonbuk, 460000=Jeonnam, 470000=Gyeongbuk, 480000=Gyeongnam, "
            "500000=Jeju."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "sido_cd": {
                    "type": "string",
                    "pattern": "^\\d{6}$",
                    "description": "HIRA SIDO 6-digit code (e.g. 110000=Seoul).",
                },
                "name": {"type": "string", "description": "Hospital name partial match."},
                "num_rows": _NUM_ROWS,
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="hira_pharmacy_search",
        description=(
            "HIRA pharmacy directory search — every licensed Korean pharmacy. "
            "Filter by SIDO code and/or name partial match."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "sido_cd": {"type": "string", "pattern": "^\\d{6}$"},
                "name": {"type": "string"},
                "num_rows": _NUM_ROWS,
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="hira_hospital_nearby",
        description=(
            "Hospitals within a radius of a coordinate (WGS84). Default radius "
            "3 km, max 20 km. Returns hospitals sorted by distance with phone, "
            "address, and HIRA classification."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "lat": _LAT,
                "lng": _LNG,
                "radius_km": {
                    "type": "number",
                    "minimum": 0.5,
                    "maximum": 20,
                    "default": 3.0,
                },
            },
            "required": ["lat", "lng"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="nmc_night_pharmacies",
        description=(
            "Night- and holiday-shift pharmacies (operating hours included). "
            "Filter by SIDO and SIGUNGU Korean name. Source: NMC E-gen."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "sido": {
                    "type": "string",
                    "description": "SIDO Korean name (e.g. 서울특별시, 부산광역시).",
                },
                "sigungu": {
                    "type": "string",
                    "description": "SIGUNGU Korean name (e.g. 강남구).",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="nmc_er_realtime",
        description=(
            "Real-time emergency-room availability (open beds, CT, MRI, key "
            "speciality acceptance) at every Korean ER. 5-minute backend cache. "
            "Critical for triage decisions and travel-medicine planning."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "sido": {
                    "type": "string",
                    "description": "SIDO Korean name (default 서울특별시).",
                },
                "sigungu": {"type": "string"},
                "num_rows": {"type": "integer", "minimum": 1, "maximum": 200, "default": 50},
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="nmc_trauma_centers",
        description=(
            "Korea regional and local trauma centers (권역·지역 외상센터). "
            "Returns name, address, designation level. 6-hour backend cache."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "num_rows": {"type": "integer", "minimum": 1, "maximum": 200, "default": 50},
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
    "hira_hospital_search": _h(
        "healthcare/hospitals",
        lambda a: {
            "sido_cd": a.get("sido_cd"),
            "name": a.get("name"),
            "num_rows": a.get("num_rows"),
        },
    ),
    "hira_pharmacy_search": _h(
        "healthcare/pharmacies",
        lambda a: {
            "sido_cd": a.get("sido_cd"),
            "name": a.get("name"),
            "num_rows": a.get("num_rows"),
        },
    ),
    "hira_hospital_nearby": _h(
        "healthcare/hospitals/nearby",
        lambda a: {
            "lat": a.get("lat"),
            "lng": a.get("lng"),
            "radius_km": a.get("radius_km"),
        },
    ),
    "nmc_night_pharmacies": _h(
        "healthcare/night-pharmacies",
        lambda a: {"sido": a.get("sido"), "sigungu": a.get("sigungu")},
    ),
    "nmc_er_realtime": _h(
        "healthcare/er-live",
        lambda a: {
            "sido": a.get("sido"),
            "sigungu": a.get("sigungu"),
            "num_rows": a.get("num_rows"),
        },
    ),
    "nmc_trauma_centers": _h(
        "healthcare/trauma-centers",
        lambda a: {"num_rows": a.get("num_rows")},
    ),
}
