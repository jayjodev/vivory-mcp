"""Shared HTTP client for the Vivory Korea Data Gateway.

The umbrella server makes all upstream calls to api.vivory.app/api/public-tools/*.
Each sub-source (KOSIS / ECOS / NEIS / ...) is just a different URL path;
the auth, caching, attribution, and JS-literal parsing all live on the
backend (api.vivory.app). The MCP layer only translates LLM tool calls
into HTTP GETs.

Self-hosting: set `VIVORY_API_BASE` to override the default endpoint.
"""
from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_API_BASE = "https://api.vivory.app/api"
TIMEOUT = httpx.Timeout(30.0, connect=10.0)
USER_AGENT = "vivory-mcp-korea/0.4.0 (+https://vivory.app)"


def get_api_base() -> str:
    return (os.environ.get("VIVORY_API_BASE") or DEFAULT_API_BASE).rstrip("/")


def get_api_key() -> str | None:
    """Optional Vivory API key for tier upgrade (free 100/day → pro 10k/day → enterprise 100k/day).

    Sign up at https://api.vivory.app/dashboard/api-keys. The MCP server runs
    fine without a key (anonymous tier, 100 calls/day per source IP).
    """
    raw = os.environ.get("VIVORY_API_KEY")
    return raw.strip() if raw and raw.strip() else None


_client: httpx.AsyncClient | None = None


def _build_headers() -> dict[str, str]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    api_key = get_api_key()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


async def get_client() -> httpx.AsyncClient:
    """Singleton async httpx client."""
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            base_url=get_api_base(),
            timeout=TIMEOUT,
            headers=_build_headers(),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            follow_redirects=True,
        )
    return _client


async def get(path: str, params: dict[str, Any] | None = None) -> dict | list:
    """GET /api/public-tools/{path} → parsed JSON."""
    client = await get_client()
    clean = {k: v for k, v in (params or {}).items() if v is not None}
    resp = await client.get(f"/public-tools/{path.lstrip('/')}", params=clean)
    if resp.status_code == 429:
        raise RuntimeError(
            "Vivory rate limit exceeded — "
            "anonymous tier is 100/day per IP. Set VIVORY_API_KEY (sign up at "
            "https://api.vivory.app/dashboard/api-keys) to upgrade."
        )
    if resp.status_code == 401:
        raise RuntimeError(
            "Vivory API key rejected — verify VIVORY_API_KEY against "
            "https://api.vivory.app/dashboard/api-keys."
        )
    resp.raise_for_status()
    return resp.json()
