"""Media + document provenance tools — receipt / integrity backbone.

Trimmed to the moat in v0.14.0 (2026-06-05). The full Phase A cluster (EXIF,
perceptual hash, video metadata/frame hash, PDF metadata/provenance, watermark,
RFC 3161 timestamp, AI-generator signature) was retired with the commodity-tool
cut. What stays is the offline-verifiable **receipt** backbone — the literal
substance of "See for yourself":

- verify_c2pa     — media authenticity (Content Authenticity Initiative manifest)
- compute_file_hash — universal content fingerprint (SHA-256/512 + IPFS CID v1)
- verify_hash_chain — sequence integrity for a receipt / execution trail

All standards-backed, zero new Python deps. Honest scope: signature/hash match
only; absence of a manifest does NOT prove human-made.

Backed by /api/verify/{c2pa, file-hash, hash-chain} on api.vivory.app.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_IMAGE_URL = {
    "type": "string",
    "format": "uri",
    "minLength": 8,
    "maxLength": 2000,
    "description": "Public URL to an image (jpg / png / webp / heic / gif). Max 12MB.",
}

_ANY_URL = {
    "type": "string",
    "format": "uri",
    "minLength": 8,
    "maxLength": 2000,
    "description": "Public URL to any file (image/pdf/video). Max 12MB.",
}

TOOLS: list[Tool] = [
    Tool(
        name="verify_c2pa",
        description=(
            "Inspect a media file's C2PA (Content Authenticity Initiative) "
            "manifest. Works on images, video, and audio that carry JUMBF / "
            "ISOBMFF c2pa boxes. Returns whether C2PA metadata is present, "
            "the signing actor (camera maker / editor app / AI generator), "
            "the action trail (captured / edited / generated-by-AI), and "
            "signature validity. The standard for verifying whether a media "
            "asset was AI-generated, edited, or original. Returns 'no_c2pa' "
            "cleanly when the file carries no manifest. Note: C2PA absence "
            "does NOT prove human-made — most AI generators do not sign yet."
        ),
        inputSchema={
            "type": "object",
            "properties": {"image_url": _IMAGE_URL},
            "required": ["image_url"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="verify_hash_chain",
        description=(
            "Verify the integrity of a sequential hash chain. Each item "
            "must include {content, prev_hash, hash}. Returns chain_valid "
            "boolean, first_break_index when broken, and a per-item "
            "verdict. Useful for chat logs, multi-step tool execution "
            "trails, or any sequence where 'has any prior step been "
            "tampered with?' is the question. SHA-256 only (blake3 = Phase 2)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 10000,
                    "items": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "prev_hash": {"type": "string"},
                            "hash": {"type": "string"},
                        },
                        "required": ["content", "hash"],
                        "additionalProperties": True,
                    },
                },
                "algorithm": {
                    "type": "string",
                    "enum": ["sha256", "blake3"],
                    "default": "sha256",
                },
            },
            "required": ["items"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="compute_file_hash",
        description=(
            "Multi-algorithm content fingerprint for any blob. Returns "
            "SHA-256 (hex), SHA-512 (hex), and IPFS CID v1 (raw codec, "
            "sha2-256, base32 lowercase — the 'bafkrei...' format). The "
            "CID is interoperable with IPFS, libp2p, and most "
            "decentralized content stores. Use to establish a universal "
            "identity for an artifact that any party can independently "
            "recompute and verify."
        ),
        inputSchema={
            "type": "object",
            "properties": {"file_url": _ANY_URL},
            "required": ["file_url"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_c2pa": lambda a: ("POST", "verify/c2pa", None, {"image_url": a.get("image_url")}),
    "verify_hash_chain": lambda a: (
        "POST",
        "verify/hash-chain",
        None,
        {
            "items": a.get("items") or [],
            "algorithm": a.get("algorithm") or "sha256",
        },
    ),
    "compute_file_hash": lambda a: (
        "POST",
        "verify/file-hash",
        None,
        {"file_url": a.get("file_url")},
    ),
}
