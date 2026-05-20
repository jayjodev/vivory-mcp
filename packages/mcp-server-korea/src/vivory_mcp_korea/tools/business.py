"""Korean business registration verification — NTS (국세청).

A single high-value Korean-specific verification primitive: given a
10-digit Korean business registration number, return checksum validity
and (when the gateway has NTS_SERVICE_KEY configured) the live 국세청
status — 계속사업자 / 휴업자 / 폐업자 — plus tax type and last change
date. Use cases an agent will hit: vendor onboarding, invoice issuance,
contract review.

Backed by /api/public-tools/business-number/validate on api.vivory.app.
Algorithm reference: NTS official checksum (가중치 곱셈 + modulo 10).
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="nts_business_validator",
        description=(
            "Validate a Korean business registration number (사업자등록번호) "
            "by checksum and — when the gateway has the upstream 국세청 "
            "(NTS) key — live status lookup. Returns: valid (bool), "
            "formatted (123-45-67890), business_status (계속사업자/휴업자/"
            "폐업자), business_type (일반과세자/간이과세자/면세사업자), "
            "tax_type_change_date. **Always** verify before issuing a "
            "tax invoice or onboarding a Korean vendor — checksum alone "
            "catches most typos; the NTS live lookup catches closed "
            "businesses (휴업/폐업). Free Vivory anonymous tier 100/day."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "number": {
                    "type": "string",
                    "minLength": 10,
                    "maxLength": 20,
                    "description": (
                        "10-digit Korean business registration number — "
                        "dashes optional ('1234567890' or '123-45-67890')."
                    ),
                },
            },
            "required": ["number"],
            "additionalProperties": False,
        },
    ),
]


def _h(path: str, builder: Callable[[dict], dict] = lambda a: {}) -> Callable[[dict], tuple[str, dict]]:
    def handler(args: dict) -> tuple[str, dict]:
        return path, builder(args)
    return handler


HANDLERS: dict[str, Callable[[dict], tuple[str, dict]]] = {
    "nts_business_validator": _h(
        "business-number/validate",
        lambda a: {"number": a.get("number")},
    ),
}
