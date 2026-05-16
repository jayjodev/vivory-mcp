"""Vivory KOSIS MCP server — 15 tools wrapping api.vivory.app/api/public-tools/kosis/*.

Tool categories:
  Discovery (활용분야 신청 무관, AI agent 친화):
    - kosis_categories                — 16 ROOT categories (인구/노동/CPI/GDP 등)
    - kosis_category_indicators       — listId 별 핵심지표 목록
    - kosis_indicators_search         — 지표명 키워드 검색 (statJipyoId 발견)
    - kosis_indicator_timeseries      — jipyoId/jipyoNm 기반 시계열 값
    - kosis_table_search              — 통합검색 (TBL_ID/ORG_ID 발견)

  Pre-built indicators (활용분야 신청 시 작동):
    - kosis_population                — 행정구역별 인구
    - kosis_gdp                       — 국민계정 분기 GDP
    - kosis_employment                — 경제활동인구·실업률
    - kosis_cpi                       — 소비자물가지수
    - kosis_household_income          — 가계동향 분위별
    - kosis_trade_balance             — 무역수지

  Meta (활용분야 무관):
    - kosis_table_meta                — 통계표 메타 (TBL/ORG/PRD/ITM/...)
    - kosis_table_explanation         — 통계조사 설명 (조사목적·법적근거 등)
    - kosis_statistic_tree            — 통계목록 트리 탐색

  Aggregate:
    - kosis_key_indicators            — 6 핵심지표 묶음 응답
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from . import client

logger = logging.getLogger("vivory_mcp_kosis")

server: Server = Server("vivory-mcp-kosis")


# ── Tool catalog ─────────────────────────────────────────────────

TOOLS: list[Tool] = [
    # Discovery
    Tool(
        name="kosis_categories",
        description=(
            "List the 16 ROOT categories of KOSIS Key Statistical Indicators "
            "(통계주요지표). Returns category codes (A–P) with Korean and "
            "English names. Use this first to discover what indicator domains "
            "are available, then call kosis_category_indicators with a list_id. "
            "No arguments required."
        ),
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    Tool(
        name="kosis_category_indicators",
        description=(
            "List all indicators inside a KOSIS category (listId). Each indicator "
            "has an indicator_id (statJipyoId / repJipyoId) usable in "
            "kosis_indicator_timeseries to fetch actual time-series values. "
            "Common list_ids: A=Population, C=Labor, D=Income/Consumption, "
            "M=Wages/Prices(CPI), N=National Accounts(GDP), O=Finance/Trade. "
            "Works without any 활용분야 (subscription field) registration."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "list_id": {
                    "type": "string",
                    "description": "Category code A–P (use kosis_categories to list).",
                    "pattern": "^[A-P]$",
                },
                "num_of_rows": {
                    "type": "integer",
                    "description": "Max indicators to return (default 50, max 200).",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 50,
                },
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
            "data range. Use to find indicator_id when you know the indicator "
            "name (e.g. '추계인구', '경제활동인구', '소비자물가'). Subscription-free."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Indicator name keyword in Korean (e.g. '인구', '실업률', 'GDP').",
                    "minLength": 1,
                },
                "num_of_rows": {
                    "type": "integer",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 100,
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_indicator_timeseries",
        description=(
            "Fetch time-series values for a KOSIS Key Indicator by indicator_id "
            "OR indicator_name. Provide start_period and end_period in the format "
            "matching the indicator's periodicity: YYYY (annual), YYYYMM (monthly), "
            "YYYYQ1–YYYYQ4 (quarterly). Time params are practically required. "
            "Subscription-free — works without 활용분야 registration. "
            "Use kosis_indicators_search or kosis_category_indicators first to "
            "find a valid indicator_id."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "indicator_id": {
                    "type": "string",
                    "description": "statJipyoId / repJipyoId (e.g. '618'=추계인구, '1931'=GDP).",
                },
                "indicator_name": {
                    "type": "string",
                    "description": "Korean indicator name (alternative to indicator_id).",
                },
                "start_period": {
                    "type": "string",
                    "description": "Start period — YYYY/YYYYMM/YYYYQ1 format.",
                },
                "end_period": {
                    "type": "string",
                    "description": "End period — YYYY/YYYYMM/YYYYQ4 format.",
                },
                "num_of_rows": {
                    "type": "integer",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 500,
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_table_search",
        description=(
            "Full-text search across the entire KOSIS catalog by Korean keyword. "
            "Returns matching statistical tables with tbl_id, org_id, "
            "view_path, period range, and direct KOSIS URLs. Use when you need "
            "raw tables, not curated key indicators. Subscription-free."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Search keyword in Korean (e.g. '인구', '아파트 매매').",
                    "minLength": 1,
                },
                "sort": {
                    "type": "string",
                    "enum": ["RANK", "DATE"],
                    "default": "RANK",
                    "description": "RANK=relevance, DATE=newest first.",
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                },
            },
            "required": ["q"],
            "additionalProperties": False,
        },
    ),

    # Pre-built indicators (subscription required)
    Tool(
        name="kosis_population",
        description=(
            "Korea total population by administrative region (시군구별 성별 인구수). "
            "Annual data from KOSIS table DT_1B040A3, 통계청. Use for nationwide "
            "or regional population analysis."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "years": {
                    "type": "integer",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 50,
                    "description": "Most recent N years.",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_gdp",
        description=(
            "Korea quarterly GDP and national accounts main indicators "
            "(KOSIS table DT_200Y001, BoK mirror). Real and nominal GDP."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "quarters": {
                    "type": "integer",
                    "default": 12,
                    "minimum": 1,
                    "maximum": 40,
                    "description": "Most recent N quarters.",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_employment",
        description=(
            "Korea Economic Activity Population Survey — unemployment rate, "
            "employment rate, labor force participation (monthly, KOSIS DT_1DA7001S)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "months": {
                    "type": "integer",
                    "default": 24,
                    "minimum": 1,
                    "maximum": 120,
                    "description": "Most recent N months.",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_cpi",
        description=(
            "Korea Consumer Price Index — overall, food, core CPI (monthly, "
            "KOSIS DT_1J17001). Subscription-required (물가·가계 분야)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "months": {
                    "type": "integer",
                    "default": 24,
                    "minimum": 1,
                    "maximum": 120,
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_household_income",
        description=(
            "Korea Household Income & Expenditure Survey by income decile "
            "(quarterly, KOSIS DT_1L9H008). Subscription-required (가계·복지 분야)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "quarters": {
                    "type": "integer",
                    "default": 8,
                    "minimum": 1,
                    "maximum": 40,
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_trade_balance",
        description=(
            "Korea trade balance — exports, imports, net exports (monthly, "
            "Korea Customs Service mirror, KOSIS DT_1R11006). "
            "Subscription-required (무역·국제수지 분야)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "months": {
                    "type": "integer",
                    "default": 24,
                    "minimum": 1,
                    "maximum": 120,
                },
            },
            "additionalProperties": False,
        },
    ),

    # Meta
    Tool(
        name="kosis_table_meta",
        description=(
            "Fetch metadata for a specific KOSIS table — column types: "
            "TBL (table name), ORG (organization), PRD (period info), "
            "ITM (classification/items), CMMT (annotations), UNIT (units), "
            "SOURCE (source attribution), WGT (weights), NCD (last update date). "
            "Use to understand a table's structure before querying its data."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["TBL", "ORG", "PRD", "ITM", "CMMT", "UNIT", "SOURCE", "WGT", "NCD"],
                    "description": "Metadata type.",
                },
                "org_id": {
                    "type": "string",
                    "description": "Organization code (e.g. '101'=통계청).",
                },
                "tbl_id": {
                    "type": "string",
                    "description": "Table ID (e.g. 'DT_1B040A3').",
                },
            },
            "required": ["type", "org_id", "tbl_id"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kosis_table_explanation",
        description=(
            "Fetch survey methodology / explanatory note for a KOSIS statistical "
            "investigation — survey purpose, legal basis, periodicity, "
            "methodology. Provide either stat_id alone OR (org_id + tbl_id)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "stat_id": {"type": "string", "description": "Statistical investigation ID."},
                "org_id": {"type": "string", "description": "Organization code."},
                "tbl_id": {"type": "string", "description": "Table ID."},
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
            "Browse the KOSIS hierarchical statistic tree (통계목록). Provide a "
            "parent_id (start with 'A'/'B'/... at ROOT). Service views: "
            "MT_ZTITLE=by topic, MT_OTITLE=by organization, MT_ETITLE=English KOSIS."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "parent_id": {
                    "type": "string",
                    "default": "A",
                    "description": "Parent list ID (ROOT='A','B',...).",
                },
                "vw_cd": {
                    "type": "string",
                    "default": "MT_ZTITLE",
                    "description": "Service view (MT_ZTITLE, MT_OTITLE, MT_ETITLE, etc.).",
                },
            },
            "additionalProperties": False,
        },
    ),

    # Aggregate
    Tool(
        name="kosis_key_indicators",
        description=(
            "Aggregate snapshot — fetches 6 key indicators in parallel "
            "(population, GDP, employment, CPI, household income, trade balance). "
            "Returns one combined response. Useful for a Korea macro overview "
            "dashboard. Some indicators may show 'subscription required' if "
            "the underlying API key lacks that 활용분야."
        ),
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
]


# ── MCP server handlers ──────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    args = arguments or {}

    # Map tool name → (path, query-builder)
    handlers: dict[str, tuple[str, Any]] = {
        "kosis_categories": ("categories", lambda a: {}),
        "kosis_category_indicators": (
            f"categories/{args.get('list_id', '')}",
            lambda a: {"num_of_rows": a.get("num_of_rows")},
        ),
        "kosis_indicators_search": (
            "indicators/search",
            lambda a: {"name": a.get("name"), "num_of_rows": a.get("num_of_rows")},
        ),
        "kosis_indicator_timeseries": (
            "indicators/timeseries",
            lambda a: {
                "indicator_id": a.get("indicator_id"),
                "indicator_name": a.get("indicator_name"),
                "start_period": a.get("start_period"),
                "end_period": a.get("end_period"),
                "num_of_rows": a.get("num_of_rows"),
            },
        ),
        "kosis_table_search": (
            "search",
            lambda a: {"q": a.get("q"), "sort": a.get("sort"), "limit": a.get("limit")},
        ),
        "kosis_population": ("population", lambda a: {"years": a.get("years")}),
        "kosis_gdp": ("gdp", lambda a: {"quarters": a.get("quarters")}),
        "kosis_employment": ("employment", lambda a: {"months": a.get("months")}),
        "kosis_cpi": ("cpi", lambda a: {"months": a.get("months")}),
        "kosis_household_income": ("household-income", lambda a: {"quarters": a.get("quarters")}),
        "kosis_trade_balance": ("trade-balance", lambda a: {"months": a.get("months")}),
        "kosis_table_meta": (
            f"meta/{args.get('type', '')}",
            lambda a: {"org_id": a.get("org_id"), "tbl_id": a.get("tbl_id")},
        ),
        "kosis_table_explanation": (
            "explanation",
            lambda a: {
                "stat_id": a.get("stat_id"),
                "org_id": a.get("org_id"),
                "tbl_id": a.get("tbl_id"),
            },
        ),
        "kosis_statistic_tree": (
            "tree",
            lambda a: {"parent_id": a.get("parent_id"), "vw_cd": a.get("vw_cd")},
        ),
        "kosis_key_indicators": ("key-indicators", lambda a: {}),
    }

    if name not in handlers:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    path, build_params = handlers[name]
    params = build_params(args)

    try:
        data = await client.get(path, params)
    except Exception as exc:
        logger.exception("tool %s failed", name)
        return [TextContent(
            type="text",
            text=f"Vivory KOSIS gateway error ({type(exc).__name__}): {exc}",
        )]

    return [TextContent(type="text", text=json.dumps(data, ensure_ascii=False, indent=2))]


async def run() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit):
        pass
