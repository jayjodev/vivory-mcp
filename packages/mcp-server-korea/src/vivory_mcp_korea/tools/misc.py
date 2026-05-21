"""Miscellaneous Korean public-data tools — food (MFDS) + public restroom (MOIS LOCALDATA) + school (NEIS) + living-weather (KMA).

One module groups single-endpoint sources to keep the umbrella import surface tight.
Backed by /api/public-tools/{food-nutrition,restroom,school,living-weather}/* on api.vivory.app.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="mfds_food_nutrition_search",
        description=(
            "Search Korean food nutrition database (MFDS — 식품의약품안전처). "
            "Returns calories, macronutrients, vitamins, minerals per 100g. "
            "One of `name` or `maker` is required."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Food name partial match (Korean — e.g. 김치, 라면).",
                },
                "maker": {
                    "type": "string",
                    "description": "Manufacturer partial match.",
                },
                "num_rows": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 50,
                },
            },
            "anyOf": [
                {"required": ["name"]},
                {"required": ["maker"]},
            ],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="mois_public_restrooms",
        description=(
            "Korean public restrooms (~50,000 entries) by address. Source: MOIS "
            "(행정안전부) LOCALDATA. Filter by Korean address partial match "
            "(e.g. 서울특별시, 서울특별시 강남구). Useful for travel-medicine and "
            "accessibility planning."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "addr": {
                    "type": "string",
                    "description": "Address partial match (Korean).",
                },
                "max_pages": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 3,
                    "description": "Max pages to fetch (500 entries per page).",
                },
            },
            "additionalProperties": False,
        },
    ),
    # NOTE: neis_school_search removed v0.6.0 — NEIS 약관 *재판매·벌크 덤프
    # 금지* 명시 위반. 12,555개 학교 *검색 자체*가 벌크 경로. 필요 시 단건
    # 학교 verdict (실재 + 운영 중) 형태로 verification MCP 에 재추가 검토.
    Tool(
        name="kma_living_weather",
        description=(
            "All six KMA living-weather indices in one call: UV, sensible "
            "temperature, food-poisoning risk, air-diffusion, pollen, frostbite. "
            "Provide either `area_no` (10-digit dong code, e.g. 1168000000 = "
            "Gangnam-gu Seoul) or `city` Korean name (e.g. 강남구)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "area_no": {
                    "type": "string",
                    "pattern": "^\\d{10}$",
                    "description": "Administrative dong 10-digit code.",
                },
                "city": {
                    "type": "string",
                    "description": "City / SIGUNGU Korean name.",
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
    "mfds_food_nutrition_search": _h(
        "food-nutrition/search",
        lambda a: {
            "name": a.get("name"),
            "maker": a.get("maker"),
            "num_rows": a.get("num_rows"),
        },
    ),
    "mois_public_restrooms": _h(
        "restroom/region",
        lambda a: {"addr": a.get("addr"), "max_pages": a.get("max_pages")},
    ),
    # neis_school_search handler removed v0.6.0 (see TOOLS comment above)
    "kma_living_weather": _h(
        "living-weather/all",
        lambda a: {"area_no": a.get("area_no"), "city": a.get("city")},
    ),
}
