"""Product + drug recall / safety alert verification.

When someone claims "this drug / this product was recalled", the cheapest
verification is to ask the source-of-truth recall feed. This cluster
wraps:

- openFDA drug enforcement reports (api.fda.gov/drug/enforcement.json)
- openFDA device recalls (api.fda.gov/device/recall.json)
- CPSC SaferProducts consumer-product recalls (saferproducts.gov REST)
- MFDS 의약품 회수 (Korea, via data.go.kr — scaffold if MFDS_RECALL_KEY
  not configured)

All four sources are public. openFDA + CPSC require no API key (FDA gives
240 req/min anonymous, 120k/day with optional key).

Backed by /api/verify/recall/*. Anti-mission #3 alignment: "이 약은 안전
하다" claims should chain through this before publication.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="drug_recall_check",
        description=(
            "Look up active drug recalls / enforcement reports by drug name, "
            "manufacturer, or NDC code. Returns most-recent matching recalls "
            "(default 10) with class (I/II/III), reason, status, recall date. "
            "Use to verify any 'this medication is safe' / 'this brand has "
            "no issues' claim. Sources: openFDA drug enforcement (US) + MFDS "
            "(Korea, when keyed)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 200,
                    "description": (
                        "Drug name (brand or generic), manufacturer, or NDC code "
                        "('0046-1108')."
                    ),
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "kr", "all"],
                    "default": "all",
                    "description": (
                        "Jurisdiction filter: us (openFDA), kr (MFDS), or all."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="product_recall_check",
        description=(
            "Look up consumer-product recalls + medical-device recalls by "
            "product name, brand, or manufacturer. Returns matches across "
            "CPSC (US Consumer Product Safety Commission) and openFDA device "
            "recall feeds, with hazard, remedy, and recall date. Use before "
            "endorsing or recommending a product."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 200,
                    "description": "Product / brand / manufacturer name.",
                },
                "scope": {
                    "type": "string",
                    "enum": ["all", "consumer", "device"],
                    "default": "all",
                    "description": (
                        "all = CPSC + openFDA device; consumer = CPSC only; "
                        "device = openFDA device only."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "drug_recall_check": lambda a: (
        "GET",
        "verify/recall/drug",
        {
            "query": a.get("query"),
            "country": a.get("country") or "all",
            "limit": a.get("limit") or 10,
        },
        None,
    ),
    "product_recall_check": lambda a: (
        "GET",
        "verify/recall/product",
        {
            "query": a.get("query"),
            "scope": a.get("scope") or "all",
            "limit": a.get("limit") or 10,
        },
        None,
    ),
}
