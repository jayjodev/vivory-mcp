"""DART (전자공시시스템 · opendart.fss.or.kr) tools.

Korea Financial Supervisory Service open disclosure system. Lets AI agents
look up listed-company filings, financial statements, and major shareholders.

Backed by /api/public-tools/dart/* on api.vivory.app. Non-commercial OpenAPI;
attribution mandatory (auto-injected by the gateway).

Workflow notes for the LLM:
1. Find a corp_code: call dart_company_search with a Korean or English name
   (e.g. "삼성전자" or "Samsung"). Listed companies have ticker codes; the
   8-digit corp_code is what subsequent calls need.
2. Browse filings: dart_disclosures with bgn_de/end_de date range.
3. Pull financials: dart_financials needs corp_code + bsns_year + reprt_code
   (11011=annual, 11012=H1, 11013=Q1, 11014=Q3). fs_div CFS=consolidated /
   OFS=standalone.
4. Pull shareholders: dart_major_shareholders for 5%+ holders + related
   parties (annual report only — reprt_code 11011 typically).
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_CORP_CODE = {
    "type": "string",
    "pattern": "^\\d{8}$",
    "description": "DART 8-digit corp_code (use dart_company_search to find one).",
}

_BSNS_YEAR = {
    "type": "string",
    "pattern": "^\\d{4}$",
    "description": "Business year YYYY (e.g. 2024).",
}

_REPRT_CODE = {
    "type": "string",
    "enum": ["11011", "11012", "11013", "11014"],
    "default": "11011",
    "description": "Report code: 11011=annual, 11012=half-year, 11013=Q1, 11014=Q3.",
}

TOOLS: list[Tool] = [
    Tool(
        name="dart_meta",
        description=(
            "DART gateway status: whether the upstream OpenDART key is "
            "configured, how many corp_code mappings are cached locally, and "
            "the current daily-quota usage. Useful for diagnosing why a tool "
            "call returned no data."
        ),
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    Tool(
        name="dart_company_search",
        description=(
            "Find a Korean listed-company corp_code by Korean name, English "
            "name, or ticker symbol. Returns up to N candidates with corp_code, "
            "stock_code, market segment. Default scope = listed companies "
            "(~3,500); set listed_only=false to include private filers."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 100,
                    "description": "Korean / English name or ticker (e.g. 삼성전자, Samsung, 005930).",
                },
                "listed_only": {
                    "type": "boolean",
                    "default": True,
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
            },
            "required": ["q"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="dart_company_detail",
        description=(
            "Company profile by corp_code — legal name, CEO, headquarters "
            "address, market segment (KOSPI / KOSDAQ / KONEX / non-listed), "
            "industry classification, founding date, fiscal year-end month, "
            "homepage. Includes a direct DART filing portal URL."
        ),
        inputSchema={
            "type": "object",
            "properties": {"corp_code": _CORP_CODE},
            "required": ["corp_code"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="dart_disclosures",
        description=(
            "Search DART filings by date range, company, market segment, or "
            "filing type. Use bgn_de + end_de in YYYYMMDD format; for a single "
            "day's RSS feed pass bgn_de=end_de. Filing types (pblntf_ty): "
            "A=periodic / B=major-events / C=securities-issue / D=ownership / "
            "E=fundraising / F=audits / G=corporate-governance / H=others / "
            "I=external-audits / J=foreign-companies. Market (corp_cls): "
            "Y=KOSPI / K=KOSDAQ / N=KONEX / E=non-listed."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "bgn_de": {"type": "string", "pattern": "^\\d{8}$"},
                "end_de": {"type": "string", "pattern": "^\\d{8}$"},
                "corp_code": _CORP_CODE,
                "corp_cls": {"type": "string", "enum": ["Y", "K", "N", "E"]},
                "pblntf_ty": {"type": "string", "enum": list("ABCDEFGHIJ")},
                "last_reprt_at": {
                    "type": "string",
                    "enum": ["Y"],
                    "description": "Set to Y to return only the latest amendment of each filing.",
                },
                "page_no": {"type": "integer", "minimum": 1, "default": 1},
                "page_count": {"type": "integer", "minimum": 1, "maximum": 100, "default": 50},
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="dart_financials",
        description=(
            "Financial statements for a Korean listed company — balance sheet "
            "+ income statement + 4-7 key metrics (revenue, operating profit, "
            "net income, EPS, etc.). Reports issued ~3 months after fiscal "
            "year-end (annual) or ~45 days after quarter-end (Q1/H1/Q3). "
            "fs_div CFS=consolidated (default, recommended for groups) / "
            "OFS=standalone (parent-only)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "corp_code": _CORP_CODE,
                "bsns_year": _BSNS_YEAR,
                "reprt_code": _REPRT_CODE,
                "fs_div": {
                    "type": "string",
                    "enum": ["CFS", "OFS"],
                    "default": "CFS",
                },
            },
            "required": ["corp_code", "bsns_year"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="dart_major_shareholders",
        description=(
            "Major shareholder disclosure (대주주 현황) — every party holding "
            "5%+ of voting shares plus their related parties (특수관계인) and "
            "the relation type. Sourced from the 사업보고서 (annual report); "
            "use reprt_code=11011 for canonical filing. Share count, percentage, "
            "and change-since-prior-period included."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "corp_code": _CORP_CODE,
                "bsns_year": _BSNS_YEAR,
                "reprt_code": _REPRT_CODE,
            },
            "required": ["corp_code", "bsns_year"],
            "additionalProperties": False,
        },
    ),
]


def _h(path_template: str, builder: Callable[[dict], dict] = lambda a: {}) -> Callable[[dict], tuple[str, dict]]:
    def handler(args: dict) -> tuple[str, dict]:
        return path_template.format(**args), builder(args)
    return handler


HANDLERS: dict[str, Callable[[dict], tuple[str, dict]]] = {
    "dart_meta": _h("dart/meta"),
    "dart_company_search": _h(
        "dart/companies/search",
        lambda a: {
            "q": a.get("q"),
            "listed_only": a.get("listed_only"),
            "limit": a.get("limit"),
        },
    ),
    "dart_company_detail": _h("dart/companies/{corp_code}"),
    "dart_disclosures": _h(
        "dart/disclosures",
        lambda a: {
            "bgn_de": a.get("bgn_de"),
            "end_de": a.get("end_de"),
            "corp_code": a.get("corp_code"),
            "corp_cls": a.get("corp_cls"),
            "pblntf_ty": a.get("pblntf_ty"),
            "last_reprt_at": a.get("last_reprt_at"),
            "page_no": a.get("page_no"),
            "page_count": a.get("page_count"),
        },
    ),
    "dart_financials": _h(
        "dart/companies/{corp_code}/financials",
        lambda a: {
            "bsns_year": a.get("bsns_year"),
            "reprt_code": a.get("reprt_code"),
            "fs_div": a.get("fs_div"),
        },
    ),
    "dart_major_shareholders": _h(
        "dart/companies/{corp_code}/major-shareholders",
        lambda a: {
            "bsns_year": a.get("bsns_year"),
            "reprt_code": a.get("reprt_code"),
        },
    ),
}
