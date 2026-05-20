"""URL content-trail + dataset fingerprint tools.

The simplest verification primitive of all: *what bytes did this URL
return at this timestamp?* Two tools:

- `verify_url_hash` — sha256 + size + content-type + ETag for any URL.
  Pair with `wayback_capture` to also persist a Wayback snapshot.
- `verify_dataset_fingerprint` — same, plus a cheap structural probe
  (CSV row/column count, JSON top-level type, NDJSON line count). Lets
  two parties confirm they downloaded the *same* dataset without
  exchanging the full bytes.

Backed by /api/verify/url-hash + /api/verify/dataset-fingerprint on
api.vivory.app. Both cap at 25MB to protect the gateway; for larger
artifacts use the hash-chain workflow (split-and-hash).
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_URL = {
    "type": "string",
    "format": "uri",
    "minLength": 8,
    "maxLength": 4000,
    "description": "Absolute http(s) URL to fetch and hash.",
}

_MAX_BYTES = {
    "type": "integer",
    "minimum": 1024,
    "maximum": 25 * 1024 * 1024,
    "description": "Optional fetch cap in bytes (default 25 MB).",
}

TOOLS: list[Tool] = [
    Tool(
        name="verify_url_hash",
        description=(
            "Fetch a URL right now and return sha256, byte count, HTTP "
            "content-type, ETag, last-modified, status code, and a "
            "captured_at ISO timestamp. The single cheapest evidence "
            "primitive — gives two parties a way to agree they saw the "
            "exact same bytes at the same moment. Caps at 25MB; pair with "
            "wayback_capture to also persist a Wayback snapshot for "
            "long-term retention."
        ),
        inputSchema={
            "type": "object",
            "properties": {"url": _URL, "max_bytes": _MAX_BYTES},
            "required": ["url"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="verify_dataset_fingerprint",
        description=(
            "Fingerprint a dataset URL — sha256 + size + content-type + "
            "ETag + a light structural probe. The structural probe sniffs "
            "JSON (top_level kind + array/object size), NDJSON (sampled "
            "line count), CSV (column count from first row + sampled line "
            "count), and refuses binary blobs (returns kind='binary' so "
            "the caller knows to skip structural diffs). Use this when "
            "you need to verify two parties received the same dataset "
            "*and* get a one-line shape readout in the same call. Caps "
            "at 25MB."
        ),
        inputSchema={
            "type": "object",
            "properties": {"url": _URL, "max_bytes": _MAX_BYTES},
            "required": ["url"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_url_hash": lambda a: (
        "POST",
        "verify/url-hash",
        None,
        {k: v for k, v in {"url": a.get("url"), "max_bytes": a.get("max_bytes")}.items() if v is not None},
    ),
    "verify_dataset_fingerprint": lambda a: (
        "POST",
        "verify/dataset-fingerprint",
        None,
        {k: v for k, v in {"url": a.get("url"), "max_bytes": a.get("max_bytes")}.items() if v is not None},
    ),
}
