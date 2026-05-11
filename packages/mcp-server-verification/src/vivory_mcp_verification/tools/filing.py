"""SEC EDGAR filing verification tools.

EDGAR is the canonical record for US-public-company filings — the global
sister of Korea DART. Vivory wraps EDGAR submissions + XBRL company-facts
into a unified resolver: ticker (or CIK) in, citation trail out — recent
filings with accession numbers + canonical SEC URLs, plus optional
company-fact slicing for line-item claims (revenue, opex, etc.).

Backed by /api/verify/filing/* on api.vivory.app. Free tier 500 lookups/day,
Pro 10,000/day. SEC's own attribution preserved (URLs point to sec.gov
documents — Vivory only resolves + normalizes).
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_TICKER = {
    "type": "string",
    "minLength": 1,
    "maxLength": 10,
    "description": "US ticker symbol (e.g. 'AAPL', 'TSLA', 'BRK.B').",
}

_CIK = {
    "type": "string",
    "minLength": 1,
    "maxLength": 10,
    "description": "SEC Central Index Key — 1–10 digit numeric ID. Vivory zero-pads to 10 digits internally.",
}

TOOLS: list[Tool] = [
    Tool(
        name="verify_filing",
        description=(
            "Resolve a US-public-company ticker (or CIK) to {cik, name, "
            "exchange, sic, latest_filing}. Returns 'not-found' if the "
            "ticker is unrecognized. Use as the default first call on any "
            "US-listed company an LLM is about to cite — confirms the "
            "entity exists and surfaces the most-recent filing accession + "
            "canonical SEC URL. Sourced from SEC EDGAR public API."
        ),
        inputSchema={
            "type": "object",
            "properties": {"ticker": _TICKER, "cik": _CIK},
            "additionalProperties": False,
        },
    ),
    Tool(
        name="filing_recent",
        description=(
            "Return up to `limit` recent SEC filings for a CIK, optionally "
            "filtered by form type (10-K, 10-Q, 8-K, S-1, DEF 14A, etc.). "
            "Each row includes the accession number, filing date, report "
            "date, and the canonical SEC primary-document URL — the "
            "citation-trail evidence that 'this filing exists at SEC and "
            "has the accession we say it does'. Use after verify_filing "
            "when the agent needs to link to or quote a specific filing."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "cik": _CIK,
                "forms": {
                    "type": "string",
                    "maxLength": 200,
                    "description": "Comma-separated form list (e.g. '10-K,10-Q,8-K'). Omit for all.",
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
            },
            "required": ["cik"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="filing_facts",
        description=(
            "Return XBRL company facts for a CIK (US-GAAP + DEI taxonomy). "
            "Heavy by default (1MB+); pass `concept=us-gaap:Revenues` (or "
            "similar) to slice a single concept across all filing periods. "
            "Use when the agent is citing a specific line item ('Apple's "
            "FY2023 revenue was $X') and needs the SEC-filed value with "
            "period + filing accession provenance."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "cik": _CIK,
                "concept": {
                    "type": "string",
                    "maxLength": 120,
                    "description": (
                        "Optional XBRL concept in `taxonomy:Name` form "
                        "(e.g. 'us-gaap:Revenues', 'us-gaap:Assets'). "
                        "Default taxonomy = us-gaap if no colon."
                    ),
                },
            },
            "required": ["cik"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_filing": lambda a: (
        "GET",
        "verify/filing",
        {"ticker": a.get("ticker"), "cik": a.get("cik")},
        None,
    ),
    "filing_recent": lambda a: (
        "GET",
        "verify/filing/recent",
        {"cik": a.get("cik"), "forms": a.get("forms"), "limit": a.get("limit")},
        None,
    ),
    "filing_facts": lambda a: (
        "GET",
        "verify/filing/facts",
        {"cik": a.get("cik"), "concept": a.get("concept")},
        None,
    ),
}
