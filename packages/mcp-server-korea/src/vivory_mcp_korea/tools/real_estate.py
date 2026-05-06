"""MoLIT (국토교통부) real-estate tools — apartment transactions (RTMS).

Backed by /api/public-tools/real-estate/* on api.vivory.app.
MOLIT publishes transactions with ~60-day reporting lag.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_LAWD_CD = {
    "type": "string",
    "pattern": "^\\d{5}$",
    "description": "LAWD (법정동) 5-digit code, sgg level (e.g. 11680=Gangnam-gu Seoul, 11650=Seocho-gu Seoul, 26230=Haeundae-gu Busan). Use molit_region_codes to look up.",
}
_DEAL_YMD = {
    "type": "string",
    "pattern": "^\\d{6}$",
    "description": "YYYYMM (e.g. 202604). Note: most recent 60 days under-report due to MOLIT reporting lag.",
}

TOOLS: list[Tool] = [
    Tool(
        name="molit_region_codes",
        description=(
            "Look up Korean LAWD (법정동) 5-digit region codes used by MOLIT "
            "real-estate APIs. Search by Korean region name partial match."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Region name partial match (e.g. 강남, 해운대).",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="molit_apt_trade",
        description=(
            "MOLIT apartment sale (매매) transactions for a region in one month. "
            "Returns building name, deal price (한국 만원 단위), area (㎡), floor, "
            "build year. Both lawd_cd and deal_ymd are required."
        ),
        inputSchema={
            "type": "object",
            "properties": {"lawd_cd": _LAWD_CD, "deal_ymd": _DEAL_YMD},
            "required": ["lawd_cd", "deal_ymd"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="molit_apt_rent",
        description=(
            "MOLIT apartment lease (전세/월세) transactions for a region in one "
            "month. Distinguishes 전세 (deposit-only) from 월세 (deposit + monthly)."
        ),
        inputSchema={
            "type": "object",
            "properties": {"lawd_cd": _LAWD_CD, "deal_ymd": _DEAL_YMD},
            "required": ["lawd_cd", "deal_ymd"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="molit_apt_price_trend",
        description=(
            "Monthly median apartment sale price trend for a region. Returns "
            "month-by-month median, count of trades, and ±range. Useful for "
            "spotting rapid appreciation or correction."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "lawd_cd": _LAWD_CD,
                "end_ymd": {**_DEAL_YMD, "description": "Window end month YYYYMM."},
                "months": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 24,
                    "default": 6,
                    "description": "Window length in months (2~24).",
                },
            },
            "required": ["lawd_cd", "end_ymd"],
            "additionalProperties": False,
        },
    ),
]


def _h(path: str, builder: Callable[[dict], dict] = lambda a: {}) -> Callable[[dict], tuple[str, dict]]:
    def handler(args: dict) -> tuple[str, dict]:
        return path, builder(args)
    return handler


HANDLERS: dict[str, Callable[[dict], tuple[str, dict]]] = {
    "molit_region_codes": _h(
        "real-estate/regions",
        lambda a: {"q": a.get("q")},
    ),
    "molit_apt_trade": _h(
        "real-estate/apt-trade",
        lambda a: {"lawd_cd": a.get("lawd_cd"), "deal_ymd": a.get("deal_ymd")},
    ),
    "molit_apt_rent": _h(
        "real-estate/apt-rent",
        lambda a: {"lawd_cd": a.get("lawd_cd"), "deal_ymd": a.get("deal_ymd")},
    ),
    "molit_apt_price_trend": _h(
        "real-estate/apt-trend",
        lambda a: {
            "lawd_cd": a.get("lawd_cd"),
            "end_ymd": a.get("end_ymd"),
            "months": a.get("months"),
        },
    ),
}
