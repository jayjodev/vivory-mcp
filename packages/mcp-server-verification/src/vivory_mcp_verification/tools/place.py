"""OpenStreetMap Nominatim geo verification tools.

Places (cities, neighborhoods, POIs, addresses) get hallucinated by
LLMs almost as often as people — wrong coords, fabricated districts,
misspelled landmarks. OSM is the global authoritative open
gazetteer; Nominatim is the canonical name-resolution surface.

Backed by /api/verify/place + /api/verify/place/search. The gateway
throttles upstream to comply with Nominatim's ≤1 req/sec usage policy.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="verify_place",
        description=(
            "Resolve a place by OSM ID (osm_type + osm_id) or by "
            "coordinates (lat + lon) to canonical record: display name, "
            "country / state / city, address components, OSM type/class. "
            "Use after place_search picks a candidate, or to reverse-"
            "geocode a coordinate pair."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "osm_type": {
                    "type": "string",
                    "pattern": "^[NWR]$",
                    "description": "N (node) / W (way) / R (relation).",
                },
                "osm_id": {"type": "integer", "minimum": 1},
                "lat": {"type": "number", "minimum": -90, "maximum": 90},
                "lon": {"type": "number", "minimum": -180, "maximum": 180},
            },
            "anyOf": [
                {"required": ["osm_type", "osm_id"]},
                {"required": ["lat", "lon"]},
            ],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="place_search",
        description=(
            "Search OpenStreetMap Nominatim by free-text place name. "
            "Returns up to `limit` candidates with OSM IDs + coords + "
            "importance score — pick one then call verify_place. Filter "
            "by country_code to disambiguate common names."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {"type": "string", "minLength": 2, "maxLength": 200},
                "country_code": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 2,
                    "description": "ISO 3166-1 alpha-2 country filter (us, kr, jp, …).",
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 25, "default": 5},
            },
            "required": ["q"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_place": lambda a: (
        "GET",
        "verify/place",
        {"osm_type": a.get("osm_type"), "osm_id": a.get("osm_id"), "lat": a.get("lat"), "lon": a.get("lon")},
        None,
    ),
    "place_search": lambda a: (
        "GET",
        "verify/place/search",
        {"q": a.get("q"), "country_code": a.get("country_code"), "limit": a.get("limit")},
        None,
    ),
}
