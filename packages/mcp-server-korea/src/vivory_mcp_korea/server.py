"""Vivory Korea MCP — DEPRECATED as of v0.6.0.

This package is deprecated. Korean public-data raw access was removed because
it conflicted with Vivory's mission of *verifiable AI work* — raw wrappers
redistributed data rather than verified it.

Migration:
  uvx vivory-mcp-verification    # 89 tools, including Korean verdict tools

Korean verdict tools (already in verification MCP):
  - kor_law_currency       — 한국 법령 현행여부 verdict (law.go.kr)
  - kor_company_status     — KYB cross-verification (NTS + CSL)
  - doi_retraction_status  — DOI retraction (Crossref + OpenAlex + PubPeer)

Korean public-data sources (KOSIS, BOK, DART, KMA, etc.) are now used as
*underlying evidence* for verdicts inside vivory-mcp-verification — not as
raw passthrough. Authenticated with the Tools Pro $4.99/mo key.

Why this package still exists as a release:
  - Existing v0.5.0 users see a deprecation notice on first call → smooth migration.
  - No actual data is served — any tool call returns the migration payload.
  - v0.6.2: dead raw-wrapper source modules removed from wheel (were
    unused since v0.6.0 but still bundled; deleted to avoid shipping
    retired-by-ToS source code).
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

logger = logging.getLogger("vivory_mcp_korea")

server: Server = Server("vivory-korea")


_DEPRECATION_NOTICE: dict[str, Any] = {
    "status": "deprecated",
    "since": "v0.6.0",
    "replacement_package": "vivory-mcp-verification",
    "install_command": "uvx vivory-mcp-verification",
    "korean_verdict_tools_in_verification": [
        "kor_law_currency",
        "kor_company_status",
        "doi_retraction_status",
    ],
    "rationale": (
        "Korean raw-data wrappers were retired because they redistributed "
        "data rather than verified it (DART 공시 bulk, NEIS 학교 list, MOLIT "
        "거래 raw, VWorld 1,534 venue dump — all conflicted with the source "
        "terms of service). The verification MCP uses Korean sources as "
        "underlying evidence for verdicts, which is consistent with Vivory's "
        "verifiable-AI-work mission and the source ToS of each provider."
    ),
    "pricing": "Tools Pro $4.99/mo key works for vivory-mcp-verification (bundle absorb 2026-06-01; standalone $29/mo Vivory API Pro tier retired)",
    "docs": "https://api.vivory.app/mcp",
}


TOOLS: list[Tool] = [
    Tool(
        name="vivory_korea_deprecated_migration_notice",
        description=(
            "vivory-mcp-korea is DEPRECATED as of v0.6.0 — migrate to "
            "vivory-mcp-verification (Korean verdict tools included, same "
            "Pro key). Call this tool for migration details. ANY other tool "
            "call on this package returns the same deprecation payload."
        ),
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
]


HANDLERS: dict[str, Any] = {
    "vivory_korea_deprecated_migration_notice": lambda _args: _DEPRECATION_NOTICE,
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """All tool calls — including the removed v0.5 names — return the
    deprecation notice. Agents get a clear migration signal instead of
    silent 404s."""
    handler = HANDLERS.get(name)
    if handler is not None:
        envelope = handler(arguments or {})
    else:
        envelope = {
            **_DEPRECATION_NOTICE,
            "removed_tool_called": name,
            "code": "DEPRECATED",
            "gateway": "vivory-mcp-korea (deprecated)",
        }
    return [TextContent(type="text", text=json.dumps(envelope, ensure_ascii=False, indent=2))]


async def run() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def _startup_banner() -> None:
    """Loud deprecation banner — first thing existing v0.5 users see."""
    import os
    if os.environ.get("VIVORY_MCP_QUIET", "").strip() in ("1", "true", "yes"):
        return
    print(
        "[vivory-mcp-korea] ⚠ DEPRECATED v0.6.2\n"
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
