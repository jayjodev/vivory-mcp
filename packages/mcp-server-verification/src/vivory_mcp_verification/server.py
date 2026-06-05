"""Vivory Verification umbrella MCP server.

Aggregates verifiable-AI-work tools under a single MCP server name
(`vivory-verification`). v0.14.0 ships 13 tools across 4 categories — the
**moat collapse** (2026-06-05): the agent surface narrows to what only Vivory
can offer (Korean public-data verdicts + the deterministic-provenance-hash
reconcile engine + the offline-verifiable receipt backbone), dropping ~74
commodity public-API wrappers (LEI, SEC EDGAR, World Bank, USGS, DefiLlama,
Wikidata, ClinicalTrials, ORCID, npm/PyPI, sanctions, archive/wayback, …) and
the surface-internal tools (repro·peer-review tied to the now-personal Repro
Hub, forecast tied to the retired forecast surface). Web Tools keep their
breadth as an SEO discovery funnel — the parity invariant is decoupled to
`web ⊇ MCP` (MCP = the curated moat subset, see policies/verification-parity.md).

Prior retires: v0.13.0 dropped 2 forecast tools (forecast_track_record,
submit_forecast); v0.12.0 dropped 10 low-uptake tools (4 Tier-U composers +
6 parity-debt MCP-only). Bundle absorb 2026-06-01 collapsed the prior $29/mo
Vivory API Pro tier into Tools Pro $4.99/mo single key.

- law         (5) — kor_law_lookup, kor_law_currency, kor_case_search, kor_bill_status, kor_company_status (국가법령정보센터 + 열린국회정보 + NTS×CSL Verified Fact corpus — the Korean public-data moat)
- reconcile   (3) — company_reconcile, recall_reconcile, person_reconcile (cross-source 2-4 registry consensus with deterministic provenance hash — Vivory-differentiated method. LOCKED 2026-05-22)
- doi         (2) — verify_doi, doi_retraction_check (research-integrity anchor: verdict + retraction gate before an LLM cites a paper)
- provenance  (3) — verify_c2pa, verify_hash_chain, compute_file_hash (offline-verifiable receipt backbone — the substance of "See for yourself")

Architecture:
- Tool definitions live in `tools/{category}.py` per concern
- `server.py` aggregates them into a single MCP catalog
- Each handler returns (method, path, params, body); `client.request` dispatches
  to api.vivory.app/api/{path}
"""
from __future__ import annotations

import asyncio
import difflib
import json
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from . import client
from .tools import (
    doi as doi_tools,
    law as law_tools,
    provenance as provenance_tools,
    reconcile as reconcile_tools,
)

logger = logging.getLogger("vivory_mcp_verification")

server: Server = Server("vivory-verification")


TOOLS: list[Tool] = [
    *doi_tools.TOOLS,
    *provenance_tools.TOOLS,
    *law_tools.TOOLS,
    *reconcile_tools.TOOLS,
]


HANDLERS: dict[str, Any] = {
    **doi_tools.HANDLERS,
    **provenance_tools.HANDLERS,
    **law_tools.HANDLERS,
    **reconcile_tools.HANDLERS,
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


def _classify_error(exc: BaseException) -> str:
    """Map exception → stable error code for agents to branch on."""
    msg = str(exc).lower()
    if "rate limit" in msg or "429" in msg:
        return "RATE_LIMIT"
    # 422/400 from upstream = the caller's params didn't satisfy the backend
    # schema. Surface as VALIDATION (not UPSTREAM) so an agent retrying with
    # different inputs knows it's a parameter problem, not a server outage.
    if "422" in msg or "unprocessable" in msg or "400" in msg or "bad request" in msg:
        return "VALIDATION"
    if "rejected" in msg or "401" in msg or "auth" in msg:
        return "AUTH"
    if "timeout" in msg or "timed out" in msg or isinstance(exc, TimeoutError):
        return "TIMEOUT"
    if "404" in msg or "not found" in msg:
        return "NOT_FOUND"
    if isinstance(exc, ValueError):
        return "VALIDATION"
    return "UPSTREAM"


_REQUIRED_BY_TOOL: dict[str, list[str]] = {
    t.name: list(t.inputSchema.get("required", []) or [])
    for t in TOOLS
}


def _missing_required(name: str, args: dict[str, Any]) -> list[str]:
    required = _REQUIRED_BY_TOOL.get(name, [])
    return [k for k in required if k not in args or args.get(k) in (None, "")]


def _error_envelope(tool: str, exc: BaseException) -> dict[str, Any]:
    return {
        "error": f"{type(exc).__name__}: {exc}",
        "code": _classify_error(exc),
        "tool": tool,
        "gateway": "vivory-mcp-verification",
    }


def _did_you_mean(name: str, registry: dict[str, Any], k: int = 3) -> list[str]:
    """Fuzzy-match an unknown tool name against the registered catalog.

    Uses difflib.get_close_matches with a permissive cutoff so agents that
    mistype `verify_doi_metadata` → `doi_metadata` (or vice versa) get a
    useful hint instead of just `UNKNOWN_TOOL`. Returns up to k candidates,
    most-similar first.
    """
    if not name:
        return []
    return difflib.get_close_matches(name, list(registry.keys()), n=k, cutoff=0.55)


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    args = arguments or {}
    handler = HANDLERS.get(name)
    if handler is None:
        suggestions = _did_you_mean(name, HANDLERS)
        envelope = {
            "error": f"Unknown tool: {name}",
            "code": "UNKNOWN_TOOL",
            "tool": name,
            "gateway": "vivory-mcp-verification",
            "did_you_mean": suggestions,
        }
        return [TextContent(type="text", text=json.dumps(envelope, ensure_ascii=False))]

    missing = _missing_required(name, args)
    if missing:
        envelope = {
            "error": f"Missing required argument(s): {', '.join(missing)}",
            "code": "VALIDATION",
            "tool": name,
            "gateway": "vivory-mcp-verification",
            "missing": missing,
        }
        return [TextContent(type="text", text=json.dumps(envelope, ensure_ascii=False))]

    try:
        method, path, params, body = handler(args)
        data = await client.request(method, path, params=params, json_body=body)
    except Exception as exc:
        logger.exception("tool %s failed", name)
        envelope = _error_envelope(name, exc)
        return [TextContent(type="text", text=json.dumps(envelope, ensure_ascii=False))]

    return [TextContent(type="text", text=json.dumps(data, ensure_ascii=False, indent=2))]


async def run() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def _startup_banner() -> None:
    """Print tier + tool-count banner to stderr.

    Anonymous users see the upgrade path *before* hitting a 429. Pro users
    see confirmation that their key is being sent. Both surface the
    Korean verdict tools bundled here (kor_law_currency, kor_company_status,
    doi_retraction_status, …) — the prior `vivory-mcp-korea` sibling is
    deprecated and no longer pairs with this package.

    Silence with `VIVORY_MCP_QUIET=1` for embedding in IDE logs.
    """
    import os
    if os.environ.get("VIVORY_MCP_QUIET", "").strip() in ("1", "true", "yes"):
        return
    has_key = client.get_api_key() is not None
    base = client.get_api_base()
    tool_count = len(TOOLS)
    if has_key:
        print(
            f"[vivory-mcp-verification] {tool_count} tools | Pro tier (Bearer key sent) | "
            f"gateway={base} | Korean sources are bundled inside verdicts (kor_law_currency, kor_company_status, doi_retraction_status, …)",
            file=sys.stderr,
            flush=True,
        )
    else:
        print(
            f"[vivory-mcp-verification] {tool_count} tools | Anonymous tier (100/day per IP) | "
            f"gateway={base}\n"
            f"  → Tools Pro $4.99/mo single key (10k/day, no auto-renew, no custody)\n"
            f"    at https://tools.vivory.app/pro — same key authenticates both the\n"
            f"    tools.vivory.app utility surface and this Verification MCP\n"
            f"    (bundle absorb 2026-06-01). Korean sources are bundled inside\n"
            f"    verdicts (kor_law_currency, kor_company_status, doi_retraction_status, …).",
            file=sys.stderr,
            flush=True,
        )


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )
    _startup_banner()
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit):
        pass
