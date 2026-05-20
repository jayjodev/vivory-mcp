"""Korean law, case-law, and legislative bill verification.

When a Korean legal agent (or any LLM citing Korean statute) claims a law
article exists, the cheapest way to fabricate a hallucination is just to
make up a plausible-sounding article number. This cluster wraps three
first-party Korean government sources so the cite can be checked:

- 국가법령정보센터 (law.go.kr) — statute lookup by name + article. OC
  identifier required (per-user but accepts generic strings; default 'vivory').
- 종합법률정보 search redirect (glaw.scourt.go.kr) — case-law discovery surface.
  No clean JSON API; this tool returns search-result links + extracted titles.
- 열린국회정보 (open.assembly.go.kr) — legislative bill status. Requires
  per-user API key (set ASSEMBLY_OPEN_API_KEY); falls back to scaffold link.

Backed by /api/verify/law/* on api.vivory.app. Anti-mission #7-safe — all
three sources are public government endpoints; no private/PII data.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_LAW_NAME = {
    "type": "string",
    "minLength": 1,
    "maxLength": 200,
    "description": (
        "Korean law name in any common form — '민법', '형법 제250조', "
        "'개인정보 보호법'. Article ('제N조') can be embedded in name "
        "or passed separately."
    ),
}

_ARTICLE = {
    "type": "string",
    "minLength": 1,
    "maxLength": 50,
    "description": (
        "Article spec: '250', '제250조', '제250조의2', '250-2'. Optional — "
        "omit to receive law-level metadata + table of contents only."
    ),
}

TOOLS: list[Tool] = [
    Tool(
        name="kor_law_lookup",
        description=(
            "Look up a Korean statute (현행법령) by name, optionally narrowed "
            "to a single article (조). Returns law metadata (공포번호, 시행일, "
            "소관부처) and, when article is given, the article body text. "
            "Use this as the **first check** on any Korean-law citation by an "
            "LLM — if the law name does not resolve or the article number is "
            "out of range, the downstream cite is fabricated. Source: 국가"
            "법령정보센터 (law.go.kr) public OPEN API."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "law_name": _LAW_NAME,
                "article": _ARTICLE,
            },
            "required": ["law_name"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kor_case_search",
        description=(
            "Search Korean court cases (판례) by keyword via the 종합법률정보 "
            "discovery surface. Returns up to N case titles with case number "
            "(사건번호), court (법원), and detail URL on glaw.scourt.go.kr. Use "
            "to confirm that a claimed precedent exists before quoting it. "
            "Source: 대법원 종합법률정보 (glaw.scourt.go.kr)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 200,
                    "description": (
                        "Search query — case keyword or case number ('2020도1234'). "
                        "Korean or English."
                    ),
                },
                "court": {
                    "type": "string",
                    "enum": ["all", "supreme", "constitutional", "lower"],
                    "default": "all",
                    "description": (
                        "Court scope: all / 대법원 (supreme) / 헌법재판소 "
                        "(constitutional) / 하급심 (lower)."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                    "description": "Max results to return.",
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="kor_bill_status",
        description=(
            "Look up a Korean National Assembly bill (의안) by bill number or "
            "title query. Returns status (계류/통과/폐기/대안반영), proposer, "
            "committee, key dates. Use to verify claims like '이 법안이 21대 "
            "국회에서 통과되었다' against the 열린국회정보 ground truth. "
            "Source: open.assembly.go.kr. Returns scaffold + search link if "
            "ASSEMBLY_OPEN_API_KEY is not configured."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 200,
                    "description": (
                        "Bill number ('2100123') or title keyword. Bill numbers "
                        "are 7 digits where first 2 = 국회 회기 (21=21대국회)."
                    ),
                },
                "era": {
                    "type": "integer",
                    "minimum": 17,
                    "maximum": 22,
                    "description": (
                        "Optional 대수 filter (17~22). Omit to search across "
                        "all available eras."
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
    "kor_law_lookup": lambda a: (
        "GET",
        "verify/law/lookup",
        {"law_name": a.get("law_name"), "article": a.get("article")},
        None,
    ),
    "kor_case_search": lambda a: (
        "GET",
        "verify/law/case",
        {
            "query": a.get("query"),
            "court": a.get("court") or "all",
            "limit": a.get("limit") or 10,
        },
        None,
    ),
    "kor_bill_status": lambda a: (
        "GET",
        "verify/law/bill",
        {
            "query": a.get("query"),
            "era": a.get("era"),
            "limit": a.get("limit") or 10,
        },
        None,
    ),
}
