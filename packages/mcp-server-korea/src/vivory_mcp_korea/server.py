"""Vivory Korea umbrella MCP server.

Aggregates all Korean public-data tools under a single MCP server
(`vivory-korea`). v0.1 ships KOSIS only (15 tools); future versions
add ECOS, NEIS, LOCALDATA, etc. without changing the registration
command — users install once and get new tools automatically as
this package grows.

Architecture:
- Tool definitions live in `tools/{source}.py` per data source
- `server.py` aggregates them into a single MCP catalog
- HTTP routing: tool name prefix decides path
  (e.g. kosis_* → /public-tools/kosis/*, ecos_* → /public-tools/bok/*)
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
    air_quality as air_quality_tools,
    bok as bok_tools,
    business as business_tools,
    dart as dart_tools,
    healthcare as healthcare_tools,
    kosis as kosis_tools,
    misc as misc_tools,
    mobility as mobility_tools,
    opinet as opinet_tools,
    real_estate as real_estate_tools,
    tour as tour_tools,
    vworld as vworld_tools,
    weather as weather_tools,
)

logger = logging.getLogger("vivory_mcp_korea")

server: Server = Server("vivory-korea")


# Aggregate tool catalog from all sources
TOOLS: list[Tool] = [
    *kosis_tools.TOOLS,
    *bok_tools.TOOLS,
    *dart_tools.TOOLS,
    *weather_tools.TOOLS,
    *air_quality_tools.TOOLS,
    *opinet_tools.TOOLS,
    *healthcare_tools.TOOLS,
    *real_estate_tools.TOOLS,
    *tour_tools.TOOLS,
    *mobility_tools.TOOLS,
    *vworld_tools.TOOLS,
    *misc_tools.TOOLS,
    *business_tools.TOOLS,
]

# Aggregate handlers from all sources
HANDLERS: dict[str, Any] = {
    **kosis_tools.HANDLERS,
    **bok_tools.HANDLERS,
    **dart_tools.HANDLERS,
    **weather_tools.HANDLERS,
    **air_quality_tools.HANDLERS,
    **opinet_tools.HANDLERS,
    **healthcare_tools.HANDLERS,
    **real_estate_tools.HANDLERS,
    **tour_tools.HANDLERS,
    **mobility_tools.HANDLERS,
    **vworld_tools.HANDLERS,
    **misc_tools.HANDLERS,
    **business_tools.HANDLERS,
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


_ERROR_CODE_MAP = {
    "RATE_LIMIT": ("rate limit", "RATE_LIMIT"),
    "rejected": ("auth", "AUTH"),
    "Unknown tool": ("unknown_tool", "UNKNOWN_TOOL"),
}


def _classify_error(exc: BaseException) -> str:
    """Map exception → stable error code for agents to branch on."""
    msg = str(exc).lower()
    if "rate limit" in msg or "429" in msg:
        return "RATE_LIMIT"
    if "rejected" in msg or "401" in msg or "auth" in msg:
        return "AUTH"
    if "timeout" in msg or "timed out" in msg or isinstance(exc, TimeoutError):
        return "TIMEOUT"
    if "404" in msg or "not found" in msg:
        return "NOT_FOUND"
    if isinstance(exc, ValueError):
        return "VALIDATION"
    return "UPSTREAM"


def _error_envelope(tool: str, exc: BaseException) -> dict[str, Any]:
    return {
        "error": f"{type(exc).__name__}: {exc}",
        "code": _classify_error(exc),
        "tool": tool,
        "gateway": "vivory-mcp-korea",
    }


def _did_you_mean(name: str, registry: dict[str, Any], k: int = 3) -> list[str]:
    """Fuzzy-match an unknown tool name against the registered catalog."""
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
            "gateway": "vivory-mcp-korea",
            "did_you_mean": suggestions,
        }
        return [TextContent(type="text", text=json.dumps(envelope, ensure_ascii=False))]

    try:
        path, params = handler(args)
        data = await client.get(path, params)
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
    sibling Verification MCP because one $29/mo key unlocks both.

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
            f"[vivory-mcp-korea] {tool_count} tools across 16 sources | Pro tier (Bearer key sent) | "
            f"gateway={base} | sibling: `uvx vivory-mcp-verification` (same key unlocks 53 verification tools)",
            file=sys.stderr,
            flush=True,
        )
    else:
        print(
            f"[vivory-mcp-korea] {tool_count} tools across 16 sources | Anonymous tier (100/day per IP) | "
            f"gateway={base}\n"
            f"  → Upgrade to Pro 10k/day ($29/mo USDC, no auto-renew, no custody) at\n"
            f"    https://api.vivory.app/dashboard/public-api — same key unlocks the\n"
            f"    sibling `vivory-mcp-verification` (53 tools), 109 tools total.",
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
