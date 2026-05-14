"""HTTP client for Vivory KOSIS gateway (api.vivory.app/api/public-tools/kosis/*).

The MCP layer only translates LLM tool calls into HTTP GETs against our
Vivory backend. The backend handles KOSIS_API_KEY auth, Redis caching,
JS-literal parsing, attribution injection, etc.

Self-hosting: set `VIVORY_API_BASE` env var to point at your own Vivory
deployment (e.g. http://localhost:8000/api).
"""
from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_API_BASE = "https://api.vivory.app/api"
TIMEOUT = httpx.Timeout(30.0, connect=10.0)
USER_AGENT = "vivory-mcp-kosis/0.1.1 (+https://vivory.app)"


def get_api_base() -> str:
    return (os.environ.get("VIVORY_API_BASE") or DEFAULT_API_BASE).rstrip("/")


_client: httpx.AsyncClient | None = None


async def get_client() -> httpx.AsyncClient:
    """Singleton async httpx client (keep-alive across tool calls)."""
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            base_url=get_api_base(),
            timeout=TIMEOUT,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            follow_redirects=True,
        )
    return _client


async def get(path: str, params: dict[str, Any] | None = None) -> dict | list:
    """GET /api/public-tools/kosis/{path} → parsed JSON."""
    client = await get_client()
    clean = {k: v for k, v in (params or {}).items() if v is not None}
    resp = await client.get(f"/public-tools/kosis/{path.lstrip('/')}", params=clean)
    resp.raise_for_status()
    return resp.json()
