"""World Bank Open Data macro-indicator tools.

Global sister of Korea's KOSIS — World Bank publishes ~1,400 indicators
across ~270 countries, no key required. Vivory wraps the public WB API
into macro citation trail: (country, indicator, year) → canonical value
with unit, country label, and indicator label.

Common indicators:
- NY.GDP.MKTP.CD       — GDP (current US$)
- NY.GDP.PCAP.CD       — GDP per capita (current US$)
- SP.POP.TOTL          — Population, total
- FP.CPI.TOTL.ZG       — Inflation, consumer prices (annual %)
- SL.UEM.TOTL.ZS       — Unemployment, total (% of labor force)
- EN.ATM.CO2E.PC       — CO2 emissions per capita

Backed by /api/verify/indicator + /api/verify/indicator/series.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_COUNTRY = {
    "type": "string",
    "minLength": 2,
    "maxLength": 4,
    "description": "ISO 3166-1 alpha-2 or alpha-3 country code (US, USA, KR, KOR, …).",
}

_INDICATOR = {
    "type": "string",
    "minLength": 3,
    "maxLength": 40,
    "description": "World Bank indicator code (e.g. NY.GDP.MKTP.CD, SP.POP.TOTL).",
}


TOOLS: list[Tool] = [
    Tool(
        name="verify_indicator",
        description=(
            "Resolve a (country, indicator, year) tuple to the canonical "
            "World Bank value. When `year` is given returns a single "
            "observation; when omitted returns the most recent 5. Use "
            "before an LLM cites a macro statistic — confirms the value "
            "exists at the World Bank with the claimed unit + year."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "country": _COUNTRY,
                "indicator": _INDICATOR,
                "year": {"type": "integer", "minimum": 1960, "maximum": 2030},
            },
            "required": ["country", "indicator"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="indicator_series",
        description=(
            "Return a country × indicator time series for [start, end]. "
            "Use for trend verification — agent can check actual annual "
            "values without scraping a web table. Note: latest data may "
            "have 2-3 year lag for some indicators."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "country": _COUNTRY,
                "indicator": _INDICATOR,
                "start": {"type": "integer", "minimum": 1960, "maximum": 2030, "default": 2000},
                "end": {"type": "integer", "minimum": 1960, "maximum": 2030, "default": 2024},
            },
            "required": ["country", "indicator"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_indicator": lambda a: (
        "GET",
        "verify/indicator",
        {"country": a.get("country"), "indicator": a.get("indicator"), "year": a.get("year")},
        None,
    ),
    "indicator_series": lambda a: (
        "GET",
        "verify/indicator/series",
        {
            "country": a.get("country"),
            "indicator": a.get("indicator"),
            "start": a.get("start"),
            "end": a.get("end"),
        },
        None,
    ),
}
