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
    # NOTE: dart_disclosures removed v0.6.0 — bulk filing search 형태가 DART 약관의
    # 대량 다운로드 패턴에 해당. 단건 (corp_code 특정) 조회는 dart_company_detail /
    # dart_financials 가 그대로 지원.
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
    # NOTE: dart_major_shareholders removed v0.6.0 — 주주 *개인 이름* (특수관계인
    # 포함) 직접 노출은 PIPA 영역. 공시 의무 정보지만 *MCP 통한 글로벌 재배포*는
    # 별개 risk. 필요 시 verification MCP 의 verdict-only tool 로 재추가 검토.
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
    # dart_disclosures handler removed v0.6.0 (see TOOLS comment above)
    "dart_financials": _h(
        "dart/companies/{corp_code}/financials",
        lambda a: {
            "bsns_year": a.get("bsns_year"),
            "reprt_code": a.get("reprt_code"),
            "fs_div": a.get("fs_div"),
        },
    ),
    # dart_major_shareholders handler removed v0.6.0 (see TOOLS comment above)
}
