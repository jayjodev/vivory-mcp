"""Media + document provenance tools.

For checking whether an image, PDF, video, or sequence of items carries
verifiable provenance metadata. C2PA (Content Authenticity Initiative) is
the industry standard for image/video/audio provenance. PDF provenance
leans on metadata + xref + signature inspection. Hash-chain verification
is for sequence integrity (e.g. a chat log, a multi-step tool execution
trail).

Phase A (2026-05-21) adds EXIF + perceptual hash + video metadata +
video frame hash + PDF metadata + file hash + CID + AI generator
signature lookup + combined provenance summary. All standards-backed,
zero new Python deps, zero new system binaries beyond ffmpeg/ffprobe.

The four provenance axes every tool here targets:
- WHO   : signer / camera / editor / AI generator identity
- WHEN  : capture or creation timestamp (ISO 8601)
- WHERE : geolocation (EXIF GPS / ISO 6709)
- WHAT  : tool / software / codec / generator that produced the artifact

Backed by /api/verify/{c2pa, pdf-provenance, pdf-metadata, hash-chain,
watermark, timestamp, exif, perceptual-hash, video-metadata,
video-frame-hash, file-hash, ai-generator-signature, provenance-summary}
on api.vivory.app.
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

_PDF_URL = {
    "type": "string",
    "format": "uri",
    "minLength": 8,
    "maxLength": 2000,
    "description": "Public URL to a PDF. Max 12MB.",
}

_VIDEO_URL = {
    "type": "string",
    "format": "uri",
    "minLength": 8,
    "maxLength": 2000,
    "description": "Public URL to a video (mp4/mov/webm/mkv/etc). Max 12MB.",
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
        name="verify_pdf_provenance",
        description=(
            "Inspect a PDF's cryptographic provenance: digital signatures "
            "(PAdES / PKCS#7), xref-stream consistency, incremental update "
            "history (was the PDF edited after creation?). Validates each "
            "/Sig dictionary, recomputes the SHA-256 over the /ByteRange, "
            "compares it to the PKCS#7 messageDigest. Returns per-signature "
            "verdicts + tamper-likelihood score. For non-cryptographic "
            "metadata (Producer/Author/dates), use pdf_metadata instead."
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
    Tool(
        name="verify_timestamp_rfc3161",
        description=(
            "Request an RFC 3161 trusted-timestamp token from FreeTSA on "
            "an SHA-256 hex digest. Use to anchor a hash-chain receipt's "
            "tail hash to a third-party time authority. Returns the "
            "base64 TSR (DER) + parsed ISO timestamp + authority. The "
            "caller typically pairs this with verify_hash_chain to produce "
            "a tamper-evident, time-anchored receipt that any RFC 3161 "
            "client can later verify locally without depending on Vivory."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "digest_hex": {
                    "type": "string",
                    "minLength": 64,
                    "maxLength": 64,
                    "pattern": "^[0-9a-fA-F]{64}$",
                    "description": "Lowercase or uppercase hex SHA-256 digest (exactly 64 chars).",
                },
                "digest_algorithm": {
                    "type": "string",
                    "enum": ["sha256"],
                    "default": "sha256",
                    "description": "Only sha256 supported (FreeTSA limitation).",
                },
            },
            "required": ["digest_hex"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="extract_image_exif",
        description=(
            "Extract EXIF metadata + decoded GPS coordinates from an image. "
            "Returns Make / Model (camera identity), Software / "
            "ProcessingSoftware (editor identity), DateTimeOriginal "
            "(shutter time), DateTime (last-saved time), and gps.{lat, lon, "
            "alt_m, timestamp_utc} when GPS not stripped. This is the "
            "primary tool for the 'who/when/where' provenance axes on any "
            "image that carries EXIF. Note: most social-media platforms "
            "strip EXIF on upload, so absence is the common case."
        ),
        inputSchema={
            "type": "object",
            "properties": {"image_url": _IMAGE_URL},
            "required": ["image_url"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="image_perceptual_hash",
        description=(
            "Compute dHash + aHash perceptual fingerprints of an image. "
            "Both are 64-bit by default (16 hex chars). Optionally compare "
            "to a known fingerprint via Hamming distance — typical "
            "thresholds: <= 5 = same image (different compression/crop), "
            "<= 10 = visually similar, >= 25 = unrelated. Use to detect "
            "image reuse, near-duplicate detection, or to fingerprint an "
            "image for later matching against a known set. Pure-Pillow "
            "implementation (no DCT-based pHash — Phase B if needed)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "image_url": _IMAGE_URL,
                "size": {
                    "type": "integer",
                    "minimum": 4,
                    "maximum": 16,
                    "default": 8,
                    "description": "Hash grid size — size*size bits. 8 = 64-bit default.",
                },
                "compare_dhash": {
                    "type": "string",
                    "maxLength": 128,
                    "description": "Optional known dHash hex string to compute Hamming distance against.",
                },
                "compare_ahash": {
                    "type": "string",
                    "maxLength": 128,
                    "description": "Optional known aHash hex string to compute Hamming distance against.",
                },
            },
            "required": ["image_url"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="extract_video_metadata",
        description=(
            "ffprobe-backed video metadata extractor. Surfaces container "
            "(mp4/mov/mkv/etc), duration, codec for each stream, "
            "creation_time (ISOBMFF mp4 standard field), encoder string "
            "(FFmpeg vX.Y / iOS-MOV / Android), device_make / device_model "
            "(Apple QuickTime / Android tags), and ISO 6709 GPS location "
            "when present. The primary tool for the who/when/where/what "
            "axes on any video that retains metadata."
        ),
        inputSchema={
            "type": "object",
            "properties": {"video_url": _VIDEO_URL},
            "required": ["video_url"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="video_frame_hash_sample",
        description=(
            "Sample N evenly-spaced frames from a video and compute the "
            "dHash of each. Returns the dHash + timestamp for each sampled "
            "frame plus the source video duration. Use to detect whether a "
            "video is a re-encoded copy of a known video (compare the "
            "dHash sequences via Hamming distance) or to fingerprint a "
            "video for later matching. Costs one ffmpeg call per frame; "
            "default 5 frames is typically enough to distinguish copies."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "video_url": _VIDEO_URL,
                "sample_count": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 32,
                    "default": 5,
                    "description": "Number of evenly-spaced frames to hash. Default 5.",
                },
            },
            "required": ["video_url"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="extract_pdf_metadata",
        description=(
            "Extract a PDF's /Info dictionary — Title, Author, Subject, "
            "Keywords, Creator (the user-facing app — Word / LibreOffice / "
            "LaTeX), Producer (the PDF library version — Adobe PDF Library, "
            "pdfTeX, Skia), CreationDate, ModDate (both decoded to ISO "
            "8601). Plus page_count and is_encrypted. This is the "
            "*provenance metadata* (who / when / with-what-tool), distinct "
            "from verify_pdf_provenance which validates the cryptographic "
            "/Sig blob. Use both for full PDF provenance."
        ),
        inputSchema={
            "type": "object",
            "properties": {"pdf_url": _PDF_URL},
            "required": ["pdf_url"],
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
    Tool(
        name="ai_generator_signature_lookup",
        description=(
            "Match an image against a static DB of known AI-generator "
            "fingerprints (C2PA issuer keywords, EXIF Software field, raw "
            "byte patterns, PNG tEXt keys). Covers OpenAI DALL-E 3 / "
            "GPT-image-1 / Sora, Adobe Firefly, Stable Diffusion (A1111 / "
            "ComfyUI), Midjourney, Google Imagen, Black Forest FLUX, "
            "Microsoft Designer. Returns matches with confidence band "
            "(high = C2PA signed, medium = EXIF, low = byte pattern). "
            "Honest scope: signature match only. Absence of match does NOT "
            "prove human-created — most generators strip metadata. Combine "
            "with verify_c2pa + extract_image_exif + detect_watermark for "
            "a complete verdict."
        ),
        inputSchema={
            "type": "object",
            "properties": {"image_url": _IMAGE_URL},
            "required": ["image_url"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="provenance_summary",
        description=(
            "One-call combined provenance verdict across modality "
            "dimensions. Auto-detects modality (image / PDF / video) from "
            "byte signature, dispatches to the appropriate combination of "
            "C2PA + EXIF + perceptual hash + PDF metadata + signature + "
            "video ffprobe + AI generator signature, then assembles a "
            "unified report with a single rolled-up verdict "
            "(manifest_signed / metadata_only / ai_generator_matched / "
            "metadata_stripped / unknown) plus the who/when/where/what "
            "axes summarised across all signals. The recommended starting "
            "point for any 'is this real and where did it come from?' "
            "agent workflow — call this first, then drill into specific "
            "tools for axes that need more detail."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "file_url": _ANY_URL,
                "mime_hint": {
                    "type": "string",
                    "maxLength": 80,
                    "description": "Optional MIME type hint when the server fetch can't sniff reliably.",
                },
            },
            "required": ["file_url"],
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
    "verify_timestamp_rfc3161": lambda a: (
        "POST",
        "verify/timestamp",
        None,
        {
            "digest_hex": (a.get("digest_hex") or "").strip().lower(),
            "digest_algorithm": a.get("digest_algorithm") or "sha256",
        },
    ),
    "extract_image_exif": lambda a: (
        "POST",
        "verify/exif",
        None,
        {"image_url": a.get("image_url")},
    ),
    "image_perceptual_hash": lambda a: (
        "POST",
        "verify/perceptual-hash",
        None,
        {
            "image_url": a.get("image_url"),
            "size": a.get("size") or 8,
            "compare_dhash": a.get("compare_dhash"),
            "compare_ahash": a.get("compare_ahash"),
        },
    ),
    "extract_video_metadata": lambda a: (
        "POST",
        "verify/video-metadata",
        None,
        {"video_url": a.get("video_url")},
    ),
    "video_frame_hash_sample": lambda a: (
        "POST",
        "verify/video-frame-hash",
        None,
        {
            "video_url": a.get("video_url"),
            "sample_count": a.get("sample_count") or 5,
        },
    ),
    "extract_pdf_metadata": lambda a: (
        "POST",
        "verify/pdf-metadata",
        None,
        {"pdf_url": a.get("pdf_url")},
    ),
    "compute_file_hash": lambda a: (
        "POST",
        "verify/file-hash",
        None,
        {"file_url": a.get("file_url")},
    ),
    "ai_generator_signature_lookup": lambda a: (
        "POST",
        "verify/ai-generator-signature",
        None,
        {"image_url": a.get("image_url")},
    ),
    "provenance_summary": lambda a: (
        "POST",
        "verify/provenance-summary",
        None,
        {
            "file_url": a.get("file_url"),
            "mime_hint": a.get("mime_hint"),
        },
    ),
}
