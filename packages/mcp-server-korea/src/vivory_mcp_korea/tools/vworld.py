"""VWorld 공간정보 (국토교통부) — search, geocode, museum/gallery venue.

Backed by /api/public-tools/vworld/* on api.vivory.app.

Coverage:
- vworld_search    — place / address autocomplete (PLACE / ADDRESS / ROAD / DISTRICT)
- vworld_geocode   — Korean address → WGS84 (ROAD-first with PARCEL fallback)
- vworld_museums   — 박물관·미술관 1,534건 (LT_P_DGMUSEUMART), sido/sigungu filter
- vworld_museum_detail — single museum/gallery venue detail (with Google enrichment)

Attribution requirement (terms §10-3): every response carries `attribution`.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_SIDO_HINT = (
    "Korean sido (시/도). One of: 서울특별시, 부산광역시, 대구광역시, 인천광역시, "
    "광주광역시, 대전광역시, 울산광역시, 세종특별자치시, 경기도, 강원특별자치도, "
    "충청북도, 충청남도, 전북특별자치도, 전라남도, 경상북도, 경상남도, 제주특별자치도."
)

TOOLS: list[Tool] = [
    Tool(
        name="vworld_search",
        description=(
            "Korean place / address autocomplete via VWorld (국토교통부 공간정보 "
            "오픈플랫폼). Use type=PLACE for POI (e.g. 국립중앙박물관), type=ADDRESS "
            "for parcel address, type=ROAD for road-name address, type=DISTRICT for "
            "administrative region. Returns title + road/parcel addr + lat/lng."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {"type": "string", "minLength": 1, "maxLength": 80, "description": "Search query (Korean preferred)."},
                "type": {
                    "type": "string",
                    "enum": ["PLACE", "ADDRESS", "ROAD", "DISTRICT"],
                    "default": "PLACE",
                },
                "size": {"type": "integer", "minimum": 1, "maximum": 20, "default": 10},
                "page": {"type": "integer", "minimum": 1, "maximum": 10, "default": 1},
            },
            "required": ["q"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="vworld_geocode",
        description=(
            "Korean address → WGS84 lat/lng via VWorld geocoder. Tries ROAD-name "
            "address first, falls back to PARCEL (지번) address. Returns refined "
            "address + coordinates + which type matched (`type_used`)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "address": {"type": "string", "minLength": 2, "maxLength": 300, "description": "Korean address (road or parcel)."},
                "prefer": {"type": "string", "enum": ["ROAD", "PARCEL"], "default": "ROAD"},
            },
            "required": ["address"],
            "additionalProperties": False,
        },
    ),
    # NOTE: vworld_museums removed v0.6.0 — 1,534 venue bulk list 는 VWorld 약관
    # 제12조 4항 *데이터 무단 저장 금지* 와 *bulk 재배포* 해석에 걸림. 단건 조회
    # (vworld_museum_detail by venue_id) 는 fetch-on-call proxy 라 유지. life.
    # vivory.app 가 등록 도메인이므로 backend proxy 호출은 약관 정합.
    Tool(
        name="vworld_museum_detail",
        description=(
            "Single museum / gallery venue detail by Vivory venue_id. Returns the "
            "summary fields plus mgt_no (LOCALDATA 관리번호), opened_on, Google "
            "business status, Google Maps URL where available."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "venue_id": {"type": "integer", "minimum": 1, "description": "Vivory LifeVenue.id (use vworld_museums to find)."},
            },
            "required": ["venue_id"],
            "additionalProperties": False,
        },
    ),
]


def _h(path_template: str, builder: Callable[[dict], dict] = lambda a: {}) -> Callable[[dict], tuple[str, dict]]:
    def handler(args: dict) -> tuple[str, dict]:
        return path_template.format(**args), builder(args)
    return handler


HANDLERS: dict[str, Callable[[dict], tuple[str, dict]]] = {
    "vworld_search": _h(
        "vworld/search",
        lambda a: {
            "q": a.get("q"),
            "type": a.get("type"),
            "size": a.get("size"),
            "page": a.get("page"),
        },
    ),
    "vworld_geocode": _h(
        "vworld/geocode",
        lambda a: {
            "address": a.get("address"),
            "prefer": a.get("prefer"),
        },
    ),
    # vworld_museums handler removed v0.6.0 (see TOOLS comment)
    "vworld_museum_detail": _h(
        "vworld/museums/{venue_id}",
        lambda a: {},
    ),
}
