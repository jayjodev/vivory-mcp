"""AirKorea (환경부 한국환경공단) air-quality tools.

Backed by /api/public-tools/air-quality/* on api.vivory.app.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="airkorea_realtime_sido",
        description=(
            "AirKorea real-time per-station readings within a SIDO (province). "
            "Returns PM10 / PM2.5 / O3 / NO2 / SO2 / CO with KHAI grade. "
            "15-minute backend cache. Default scope = nationwide (전국)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "sido": {
                    "type": "string",
                    "description": "Korean SIDO name — 전국 (default), 서울, 부산, 인천, 대구, 광주, 대전, 울산, 경기, 강원, 충북, 충남, 전북, 전남, 경북, 경남, 제주, 세종.",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="airkorea_forecast",
        description=(
            "AirKorea air-pollution forecast issued by the Ministry of Environment. "
            "Returns regional PM2.5 / PM10 / O3 outlook for the requested date."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "inform_code": {
                    "type": "string",
                    "enum": ["PM25", "PM10", "O3"],
                    "default": "PM25",
                },
                "search_date": {
                    "type": "string",
                    "description": "YYYY-MM-DD (default: today).",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
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
    "airkorea_realtime_sido": _h(
        "air-quality/sido",
        lambda a: {"sido": a.get("sido")},
    ),
    "airkorea_forecast": _h(
        "air-quality/forecast",
        lambda a: {
            "inform_code": a.get("inform_code"),
            "search_date": a.get("search_date"),
        },
    ),
}
