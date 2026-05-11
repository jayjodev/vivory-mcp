"""Media + document provenance tools.

For checking whether an image, PDF, or sequence of items carries verifiable
provenance metadata. C2PA (Content Authenticity Initiative) is the
industry standard for image/video provenance. PDF provenance leans on
metadata + xref + signature inspection. Hash-chain verification is for
sequence integrity (e.g. a chat log, a multi-step tool execution trail).

Watermark detection is a separate axis — does this image bear a known
AI-generation watermark (Stable Diffusion / FLUX / Midjourney / etc.)?

Backed by /api/verify/c2pa, /verify/pdf-provenance, /verify/hash-chain,
/verify/watermark on api.vivory.app. These wrap Vivory's existing
c2pa-inspector / pdf-provenance / hash-chain / watermark-detector tools.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_IMAGE_URL = {
    "type": "string",
    "format": "uri",
    "minLength": 8,
    "maxLength": 2000,
    "description": "Public URL to an image (jpg / png / webp / heic). Max 50MB.",
}

_PDF_URL = {
    "type": "string",
    "format": "uri",
    "minLength": 8,
    "maxLength": 2000,
    "description": "Public URL to a PDF. Max 100MB.",
}

TOOLS: list[Tool] = [
    Tool(
        name="verify_c2pa",
        description=(
            "Inspect an image's C2PA (Content Authenticity Initiative) "
            "manifest. Returns whether C2PA metadata is present, the signing "
            "actor (camera maker / editor app / AI generator), the action "
            "trail (captured / edited / generated-by-AI), and signature "
            "validity. The standard for verifying whether an image was AI-"
            "generated, edited, or camera-original. Returns 'no_c2pa' "
            "cleanly when the image carries no manifest."
        ),
        inputSchema={
            "type": "object",
            "properties": {"image_url": _IMAGE_URL},
            "required": ["image_url"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="verify_pdf_provenance",
        description=(
            "Inspect a PDF's provenance signals: producer / creator metadata, "
            "creation + modification dates, embedded fonts, presence of "
            "digital signatures (PAdES / PKCS#7), xref-stream consistency, "
            "incremental update history (was the PDF edited after creation?). "
            "Returns a tamper-likelihood score (low / medium / high) and "
            "the specific signals contributing to it."
        ),
        inputSchema={
            "type": "object",
            "properties": {"pdf_url": _PDF_URL},
            "required": ["pdf_url"],
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
            "tampered with?' is the question."
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
        name="detect_watermark",
        description=(
            "Detect known AI-generation watermarks in an image. Checks "
            "Stable Diffusion (invisible-watermark library), Google "
            "SynthID (when surfaced), FLUX, Midjourney metadata "
            "fingerprints, plus EXIF / IPTC traces. Returns per-detector "
            "verdict + confidence. Note: absence of detected watermark "
            "does NOT prove human-created — many AI images strip watermarks "
            "or use non-watermarking models. Treat as one signal among many."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "image_url": _IMAGE_URL,
                "detectors": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["stable-diffusion", "synthid", "flux", "midjourney", "exif"],
                    },
                    "description": "Subset of detectors to run. Omit for all.",
                },
            },
            "required": ["image_url"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_c2pa": lambda a: ("POST", "verify/c2pa", None, {"image_url": a.get("image_url")}),
    "verify_pdf_provenance": lambda a: (
        "POST",
        "verify/pdf-provenance",
        None,
        {"pdf_url": a.get("pdf_url")},
    ),
    "verify_hash_chain": lambda a: (
        "POST",
        "verify/hash-chain",
        None,
        {
            "items": a.get("items") or [],
            "algorithm": a.get("algorithm") or "sha256",
        },
    ),
    "detect_watermark": lambda a: (
        "POST",
        "verify/watermark",
        None,
        {
            "image_url": a.get("image_url"),
            "detectors": a.get("detectors"),
        },
    ),
}
