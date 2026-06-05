"""Vivory KOSIS MCP — DEPRECATED as of v0.1.4.

Both this package AND the intermediate `vivory-mcp-korea` umbrella are
deprecated. Korean public-data raw access was retired because raw wrappers
redistributed data rather than verified it — conflicting with Vivory's
verifiable-AI-work mission and several upstream source ToS.

Migration (single step, drop-in):
  uvx vivory-mcp-verification

Korean verdict tools live inside vivory-mcp-verification:
  - kor_law_currency       — 한국 법령 현행여부 verdict (법령정보센터)
  - kor_company_status     — KYB cross-verification (NTS + CSL)
  - doi_retraction_status  — DOI retraction (Crossref + OpenAlex + PubPeer)

KOSIS data is now used as *underlying evidence* for verdicts inside
vivory-mcp-verification, not as raw passthrough. Tools Pro $4.99/mo key
authenticates the catalog after the 2026-06-01 bundle absorb.

This release exists only to give existing v0.1.x users a clear migration
signal on first call. Any tool name returns the same deprecation payload.
Calls to the old 15 KOSIS endpoints (kosis_categories, kosis_gdp, ...)
will NOT proxy upstream — the api.vivory.app/api/public-tools/* gateway
went cluster-internal on 2026-05-22 and returns 404 for external callers.
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

logger = logging.getLogger("vivory_mcp_kosis")

server: Server = Server("vivory-kosis")


_DEPRECATION_NOTICE: dict[str, Any] = {
    "status": "deprecated",
    "since": "v0.1.4",
    "replacement_package": "vivory-mcp-verification",
    "install_command": "uvx vivory-mcp-verification",
    "korean_verdict_tools_in_verification": [
        "kor_law_currency",
        "kor_company_status",
        "doi_retraction_status",
    ],
    "rationale": (
        "Korean raw-data wrappers (KOSIS, BOK, DART, KMA, MOLIT, VWorld, "
        "NEIS, etc.) were retired because they redistributed data rather "
        "than verified it. Several upstream sources also prohibited bulk "
        "redistribution under their ToS. The verification MCP uses Korean "
        "sources as underlying evidence for verdicts, consistent with "
        "Vivory's verifiable-AI-work mission."
    ),
    "intermediate_package_also_deprecated": "vivory-mcp-korea",
    "pricing": "Tools Pro $4.99/mo key authenticates vivory-mcp-verification (bundle absorb 2026-06-01)",
    "docs": "https://api.vivory.app/mcp",
    "upstream_gateway_status": (
        "api.vivory.app/api/public-tools/* is cluster-internal as of "
        "2026-05-22 — old KOSIS tool calls will not proxy successfully "
        "from external networks regardless of this MCP layer."
    ),
}


TOOLS: list[Tool] = [
    Tool(
        name="vivory_kosis_deprecated_migration_notice",
        description=(
            "vivory-mcp-kosis is DEPRECATED as of v0.1.4 — migrate to "
            "vivory-mcp-verification (Korean verdict tools included, same "
            "Pro key). Call this tool for migration details. ANY other "
            "tool call on this package returns the same deprecation payload."
        ),
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
]


HANDLERS: dict[str, Any] = {
    "vivory_kosis_deprecated_migration_notice": lambda _args: _DEPRECATION_NOTICE,
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """All tool calls — including the removed v0.1.x KOSIS names — return
    the deprecation notice. Agents get a clear migration signal instead of
    silent 404s from the cluster-internal upstream gateway."""
    handler = HANDLERS.get(name)
    if handler is not None:
        envelope = handler(arguments or {})
    else:
        envelope = {
            **_DEPRECATION_NOTICE,
            "removed_tool_called": name,
            "code": "DEPRECATED",
            "gateway": "vivory-mcp-kosis (deprecated)",
        }
    return [TextContent(type="text", text=json.dumps(envelope, ensure_ascii=False, indent=2))]


async def run() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def _startup_banner() -> None:
    """Loud deprecation banner — first thing existing v0.1.x users see."""
    import os
    if os.environ.get("VIVORY_MCP_QUIET", "").strip() in ("1", "true", "yes"):
        return
    print(
        "[vivory-mcp-kosis] ⚠ DEPRECATED v0.1.4\n"
        "  → migrate to:  uvx vivory-mcp-verification\n"
        "  Korean verdict tools (kor_law_currency / kor_company_status /\n"
        "  doi_retraction_status) are in vivory-mcp-verification. Same Pro key.\n"
        "  Rationale: verifiable AI work, not raw-data redistribution.",
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
