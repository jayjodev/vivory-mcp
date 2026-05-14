"""KOSIS (통계청 국가통계포털) tools — 15 tool definitions.

Mirror of `vivory-mcp-kosis` but inlined for the umbrella package so
that users can install `vivory-mcp-korea` standalone without depending
on the standalone KOSIS package. Both packages call the same backend
endpoints (`api.vivory.app/api/public-tools/kosis/*`).

Routing pattern (api_path returned by HANDLERS):
- "kosis/categories" → GET /public-tools/kosis/categories
- "kosis/population" → GET /public-tools/kosis/population
- ...etc.
"""
from __future__ import annotations

from typing import Any, Callable

from mcp.types import Tool

# ── Tool catalog ─────────────────────────────────────────────────

TOOLS: list[Tool] = [
    # Discovery
    Tool(
        name="kosis_categories",
        description=(
            "List the 16 ROOT categories of KOSIS Key Statistical Indicators "
            "(통계주요지표). Returns category codes (A–P) with Korean and "
            "English names. Use this first to discover what indicator domains "
            "are available, then call kosis_category_indicators with a list_id."
        ),
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    Tool(
        name="kosis_category_indicators",
        description=(
            "List all indicators inside a KOSIS category (listId). Each indicator "
            "has an indicator_id usable in kosis_indicator_timeseries. Common "
            "list_ids: A=Population, C=Labor, D=Income/Consumption, "
            "M=Wages/Prices(CPI), N=National Accounts(GDP), O=Finance/Trade. "
            "Subscription-free."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "list_id": {"type": "string", "pattern": "^[A-P]$"},
                "num_of_rows": {"type": "integer", "minimum": 1, "maximum": 200, "default": 50},
            },
            "required": ["list_id"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_indicators_search",
        description=(
            "Search KOSIS Key Indicators by Korean name keyword. Returns a list "
            "of matching indicators with their statJipyoId, unit, period type, "
            "data range. Subscription-free."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "num_of_rows": {"type": "integer", "default": 30, "minimum": 1, "maximum": 100},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_indicator_timeseries",
        description=(
            "Fetch time-series values for a KOSIS Key Indicator by indicator_id "
            "OR indicator_name (at least one required). Provide start_period / "
            "end_period in the format matching periodicity: YYYY (annual), "
            "YYYYMM (monthly), YYYYQ1 (quarterly)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "indicator_id": {"type": "string"},
                "indicator_name": {"type": "string"},
                "start_period": {"type": "string"},
                "end_period": {"type": "string"},
                "num_of_rows": {"type": "integer", "default": 50, "minimum": 1, "maximum": 500},
            },
            "anyOf": [
                {"required": ["indicator_id"]},
                {"required": ["indicator_name"]},
            ],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_table_search",
        description=(
            "Full-text search across the entire KOSIS catalog by Korean keyword. "
            "Returns matching tables with tbl_id, org_id, view_path, period range, "
            "and direct KOSIS URLs. Subscription-free."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {"type": "string", "minLength": 1},
                "sort": {"type": "string", "enum": ["RANK", "DATE"], "default": "RANK"},
                "limit": {"type": "integer", "default": 20, "minimum": 1, "maximum": 100},
            },
            "required": ["q"],
            "additionalProperties": False,
        },
    ),
    # Pre-built indicators
    Tool(
        name="kosis_population",
        description="Korea total population by administrative region (KOSIS DT_1B040A3, annual).",
        inputSchema={
            "type": "object",
            "properties": {"years": {"type": "integer", "default": 10, "minimum": 1, "maximum": 50}},
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_gdp",
        description="Korea quarterly GDP and national accounts main indicators (DT_200Y001).",
        inputSchema={
            "type": "object",
            "properties": {"quarters": {"type": "integer", "default": 12, "minimum": 1, "maximum": 40}},
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_employment",
        description="Korea Economic Activity Population Survey — unemployment, employment, participation (DT_1DA7001S, monthly).",
        inputSchema={
            "type": "object",
            "properties": {"months": {"type": "integer", "default": 24, "minimum": 1, "maximum": 120}},
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_cpi",
        description="Korea Consumer Price Index — overall, food, core CPI (DT_1J17001, monthly).",
        inputSchema={
            "type": "object",
            "properties": {"months": {"type": "integer", "default": 24, "minimum": 1, "maximum": 120}},
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_household_income",
        description="Korea Household Income & Expenditure Survey by income decile (DT_1L9H008, quarterly).",
        inputSchema={
            "type": "object",
            "properties": {"quarters": {"type": "integer", "default": 8, "minimum": 1, "maximum": 40}},
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_trade_balance",
        description="Korea trade balance — exports, imports, net exports (DT_1R11006, monthly).",
        inputSchema={
            "type": "object",
            "properties": {"months": {"type": "integer", "default": 24, "minimum": 1, "maximum": 120}},
            "additionalProperties": False,
        },
    ),
    # Meta
    Tool(
        name="kosis_table_meta",
        description=(
            "Fetch metadata for a specific KOSIS table — types: TBL/ORG/PRD/ITM/"
            "CMMT/UNIT/SOURCE/WGT/NCD."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["TBL", "ORG", "PRD", "ITM", "CMMT", "UNIT", "SOURCE", "WGT", "NCD"],
                },
                "org_id": {"type": "string"},
                "tbl_id": {"type": "string"},
            },
            "required": ["type", "org_id", "tbl_id"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_table_explanation",
        description="Survey methodology / explanatory note. Provide stat_id alone OR (org_id + tbl_id).",
        inputSchema={
            "type": "object",
            "properties": {
                "stat_id": {"type": "string"},
                "org_id": {"type": "string"},
                "tbl_id": {"type": "string"},
            },
            "anyOf": [
                {"required": ["stat_id"]},
                {"required": ["org_id", "tbl_id"]},
            ],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_statistic_tree",
        description=(
            "Browse the KOSIS hierarchical statistic tree. Service views: "
            "MT_ZTITLE=topic, MT_OTITLE=organization, MT_ETITLE=English KOSIS."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "parent_id": {"type": "string", "default": "A"},
                "vw_cd": {"type": "string", "default": "MT_ZTITLE"},
            },
            "additionalProperties": False,
        },
    ),
    # Aggregate
    Tool(
        name="kosis_key_indicators",
        description=(
            "Aggregate snapshot — fetches 6 key indicators in parallel "
            "(population, GDP, employment, CPI, household income, trade balance)."
        ),
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
]


# ── Handlers: tool name → (api_path, query_params builder) ──────────

def _h(path_template: str, params_builder: Callable[[dict], dict] = lambda a: {}) -> Callable[[dict], tuple[str, dict]]:
    """Build a handler. path_template may use {arg} placeholders from arguments."""
    def handler(args: dict) -> tuple[str, dict]:
        path = path_template.format(**args)
        return path, params_builder(args)
    return handler


HANDLERS: dict[str, Callable[[dict], tuple[str, dict]]] = {
    "kosis_categories": _h("kosis/categories"),
    "kosis_category_indicators": _h(
        "kosis/categories/{list_id}",
        lambda a: {"num_of_rows": a.get("num_of_rows")},
    ),
    "kosis_indicators_search": _h(
        "kosis/indicators/search",
        lambda a: {"name": a.get("name"), "num_of_rows": a.get("num_of_rows")},
    ),
    "kosis_indicator_timeseries": _h(
        "kosis/indicators/timeseries",
        lambda a: {
            "indicator_id": a.get("indicator_id"),
            "indicator_name": a.get("indicator_name"),
            "start_period": a.get("start_period"),
            "end_period": a.get("end_period"),
            "num_of_rows": a.get("num_of_rows"),
        },
    ),
    "kosis_table_search": _h(
        "kosis/search",
        lambda a: {"q": a.get("q"), "sort": a.get("sort"), "limit": a.get("limit")},
    ),
    "kosis_population": _h("kosis/population", lambda a: {"years": a.get("years")}),
    "kosis_gdp": _h("kosis/gdp", lambda a: {"quarters": a.get("quarters")}),
    "kosis_employment": _h("kosis/employment", lambda a: {"months": a.get("months")}),
    "kosis_cpi": _h("kosis/cpi", lambda a: {"months": a.get("months")}),
    "kosis_household_income": _h("kosis/household-income", lambda a: {"quarters": a.get("quarters")}),
    "kosis_trade_balance": _h("kosis/trade-balance", lambda a: {"months": a.get("months")}),
    "kosis_table_meta": _h(
        "kosis/meta/{type}",
        lambda a: {"org_id": a.get("org_id"), "tbl_id": a.get("tbl_id")},
    ),
    "kosis_table_explanation": _h(
        "kosis/explanation",
        lambda a: {
            "stat_id": a.get("stat_id"),
            "org_id": a.get("org_id"),
            "tbl_id": a.get("tbl_id"),
        },
    ),
    "kosis_statistic_tree": _h(
        "kosis/tree",
        lambda a: {"parent_id": a.get("parent_id"), "vw_cd": a.get("vw_cd")},
    ),
    "kosis_key_indicators": _h("kosis/key-indicators"),
}
