"""Shared HTTP client for the Vivory Verification Gateway.

All upstream calls go to `api.vivory.app/api/verify/*` (and a few sibling
prefixes — `/citation-trail`, `/archive`, `/research`, `/tools/receipts`).
The backend handles caching, upstream API auth (Crossref / OpenAlex /
Wayback / RetractionWatch / etc.), normalization, and attribution.
The MCP layer only translates LLM tool calls into HTTP GETs/POSTs.

Self-hosting: set `VIVORY_API_BASE` to override the default endpoint.
"""
from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_API_BASE = "https://api.vivory.app/api"
TIMEOUT = httpx.Timeout(45.0, connect=10.0)
USER_AGENT = "vivory-mcp-verification/0.6.0 (+https://vivory.app)"


def get_api_base() -> str:
    return (os.environ.get("VIVORY_API_BASE") or DEFAULT_API_BASE).rstrip("/")


def get_api_key() -> str | None:
    """Optional Vivory API key for tier upgrade.

    Anonymous (no key)            — 100 calls/day per source IP
    Tools Pro bridge ($4.99/mo)   — 1,000 calls/month (Tools Pro key)
    Vivory API Pro ($29/mo USDC)  — 10,000 calls/day, also unlocks sibling
                                    vivory-mcp-korea (124 tools total)
    Sign up at https://api.vivory.app/dashboard/public-api.
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


async def request(
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
    not_found_ok: bool = True,
) -> dict | list:
    """Generic dispatch — GET by default, POST when json_body provided.

    `not_found_ok` defaults to True for the verification gateway because most
    verify_* tools treat 404 as "no record found, claim unverified" — a
    legitimate verdict, not an error. Set to False for tools where 404
    really is an upstream failure.
    """
    client = await get_client()
    clean_params = {k: v for k, v in (params or {}).items() if v is not None}
    full_path = "/" + path.lstrip("/")
    if method.upper() == "GET":
        resp = await client.get(full_path, params=clean_params)
    elif method.upper() == "POST":
        resp = await client.post(full_path, params=clean_params, json=json_body)
    else:
        raise ValueError(f"Unsupported method: {method}")

    if resp.status_code == 429:
        raise RuntimeError(
            "Vivory rate limit exceeded — anonymous tier is 100/day per IP. "
            "Set VIVORY_API_KEY (sign up at https://api.vivory.app/dashboard) "
            "to upgrade."
        )
    if resp.status_code == 401:
        raise RuntimeError(
            "Vivory API key rejected — verify VIVORY_API_KEY against "
            "https://api.vivory.app/dashboard."
        )
    if resp.status_code == 404 and not_found_ok:
        try:
            return {"_status": 404, **(resp.json() if resp.content else {})}
        except Exception:
            return {"_status": 404, "_message": "Not found"}
    resp.raise_for_status()
    return resp.json()


async def get(path: str, params: dict[str, Any] | None = None, not_found_ok: bool = True) -> dict | list:
    return await request("GET", path, params=params, not_found_ok=not_found_ok)


async def post(path: str, json_body: dict[str, Any] | None = None, params: dict[str, Any] | None = None, not_found_ok: bool = True) -> dict | list:
    return await request("POST", path, params=params, json_body=json_body, not_found_ok=not_found_ok)
