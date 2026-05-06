"""Bank of Korea (한국은행) ECOS macro indicator tools.

Backed by /api/public-tools/bok/* on api.vivory.app.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="bok_macro_dashboard",
        description=(
            "Bank of Korea (BOK) key macroeconomic indicators in one call — "
            "policy base rate, CPI, unemployment, M2 money supply, KRW/USD "
            "exchange rate, and recent time-series. Sourced from ECOS "
            "(한국은행 경제통계시스템). Updated daily."
        ),
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
]


def _h(path: str, builder: Callable[[dict], dict] = lambda a: {}) -> Callable[[dict], tuple[str, dict]]:
    def handler(args: dict) -> tuple[str, dict]:
        return path, builder(args)
    return handler


HANDLERS: dict[str, Callable[[dict], tuple[str, dict]]] = {
    "bok_macro_dashboard": _h("bok/macro"),
}
