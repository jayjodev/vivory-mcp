"""Sanity tests for vivory-mcp-verification.

Runs offline (no httpx/network). Mirrors korea test suite — verifies:
- 98 tool count (v0.10 = v0.9 + provenance Phase A: 9 standards-backed
  who/when/where/what verification tools across image/video/PDF)
- every tool has handler returning (method, path, params, body) tuple
- inputSchema is valid JSON Schema
- error envelope is structured JSON with stable code field
  (includes `did_you_mean` fuzzy suggestion list)
- client request() supports not_found_ok parameter

Run: `pytest -q` from package root.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

import jsonschema
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vivory_mcp_verification import server as srv  # noqa: E402
from vivory_mcp_verification import client as cli  # noqa: E402


def test_tool_count_matches_version_claim():
    """v0.11.0 claims 101 tools across 37 categories (v0.10 + reconcile cluster of 3)."""
    assert len(srv.TOOLS) == 101, f"Expected 101 tools, got {len(srv.TOOLS)}"


def test_every_tool_has_handler():
    tool_names = {t.name for t in srv.TOOLS}
    handler_names = set(srv.HANDLERS.keys())
    missing = tool_names - handler_names
    extra = handler_names - tool_names
    assert not missing, f"Tools without handlers: {missing}"
    assert not extra, f"Handlers without tool definitions: {extra}"


def test_no_duplicate_tool_names():
    names = [t.name for t in srv.TOOLS]
    dupes = {n for n in names if names.count(n) > 1}
    assert not dupes, f"Duplicate tool names: {dupes}"


@pytest.mark.parametrize("tool", srv.TOOLS, ids=lambda t: t.name)
def test_input_schema_is_valid_json_schema(tool):
    schema = tool.inputSchema
    assert isinstance(schema, dict), f"{tool.name} has non-dict schema"
    assert schema.get("type") == "object", f"{tool.name} schema is not type=object"
    jsonschema.Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize("tool", srv.TOOLS, ids=lambda t: t.name)
def test_handler_returns_method_path_params_body_tuple(tool):
    """Verification handlers return (method, path, params, body)."""
    handler = srv.HANDLERS[tool.name]
    args = _placeholder_args(tool.inputSchema)
    result = handler(args)
    assert isinstance(result, tuple) and len(result) == 4, (
        f"{tool.name} handler did not return (method, path, params, body)"
    )
    method, path, params, body = result
    assert method in ("GET", "POST"), f"{tool.name} unsupported method {method!r}"
    assert isinstance(path, str) and path, f"{tool.name} returned empty path"
    assert params is None or isinstance(params, dict)
    assert body is None or isinstance(body, dict)


def test_error_envelope_unknown_tool():
    out = asyncio.run(srv.call_tool("definitely_not_a_real_tool_xyz", {}))
    assert len(out) == 1
    payload = json.loads(out[0].text)
    assert payload["code"] == "UNKNOWN_TOOL"
    assert payload["tool"] == "definitely_not_a_real_tool_xyz"
    assert payload["gateway"] == "vivory-mcp-verification"
    assert "error" in payload
    assert "did_you_mean" in payload
    assert isinstance(payload["did_you_mean"], list)


def test_did_you_mean_suggests_close_match():
    """A typo like `verify_dio` should suggest `verify_doi`."""
    out = asyncio.run(srv.call_tool("verify_dio", {}))
    payload = json.loads(out[0].text)
    assert "verify_doi" in payload["did_you_mean"], (
        f"Expected verify_doi suggestion, got {payload['did_you_mean']}"
    )


def test_did_you_mean_empty_for_garbage():
    """Random gibberish should not crash and just return [] or low-quality suggestions."""
    out = asyncio.run(srv.call_tool("xqzplv9999", {}))
    payload = json.loads(out[0].text)
    assert isinstance(payload["did_you_mean"], list)
    assert payload["code"] == "UNKNOWN_TOOL"


def test_error_classification():
    assert srv._classify_error(RuntimeError("rate limit exceeded")) == "RATE_LIMIT"
    assert srv._classify_error(RuntimeError("API key rejected")) == "AUTH"
    assert srv._classify_error(TimeoutError("timed out")) == "TIMEOUT"
    assert srv._classify_error(ValueError("bad arg")) == "VALIDATION"
    assert srv._classify_error(RuntimeError("upstream 500")) == "UPSTREAM"


def test_error_classification_422_is_validation():
    # 0.10.1: 422 Unprocessable Entity from the backend means the caller's
    # params didn't satisfy the schema — classify as VALIDATION (not UPSTREAM)
    # so an agent retrying with different inputs can branch correctly.
    assert srv._classify_error(RuntimeError("Client error '422 Unprocessable Entity'")) == "VALIDATION"
    assert srv._classify_error(RuntimeError("400 Bad Request")) == "VALIDATION"
    assert srv._classify_error(RuntimeError("Unprocessable entity")) == "VALIDATION"


def test_missing_required_args_short_circuits_with_validation_envelope():
    # 0.10.1: server validates inputSchema.required before dispatching to the
    # backend, so an agent that forgets `doi` gets a clear VALIDATION error
    # instead of a confusing UPSTREAM 422.
    out = asyncio.run(srv.call_tool("verify_doi", {}))
    payload = json.loads(out[0].text)
    assert payload["code"] == "VALIDATION"
    assert "doi" in payload.get("missing", [])
    assert "Missing required argument" in payload["error"]


def test_missing_required_treats_empty_string_as_missing():
    out = asyncio.run(srv.call_tool("verify_doi", {"doi": ""}))
    payload = json.loads(out[0].text)
    assert payload["code"] == "VALIDATION"
    assert "doi" in payload.get("missing", [])


def test_required_args_allow_dispatch():
    # Sanity: if all required args are present, validation passes through
    # (we don't actually network here — just confirm we don't trip on
    # the VALIDATION short-circuit when caller is well-formed). The handler
    # will attempt the HTTP call and likely raise during the offline test;
    # both outcomes (success envelope or UPSTREAM error) are acceptable.
    missing = srv._missing_required("verify_doi", {"doi": "10.1038/x"})
    assert missing == []


def test_api_key_format_warning(capsys, monkeypatch):
    # 0.10.1: malformed VIVORY_API_KEY (no vk_live_/vk_test_ prefix) is
    # treated as anonymous + warns once on stderr instead of being silently
    # downgraded by the backend.
    monkeypatch.setenv("VIVORY_API_KEY", "garbage_token_no_prefix")
    monkeypatch.delenv("VIVORY_MCP_QUIET", raising=False)
    cli._format_warned = False  # reset module-level guard for the test
    result = cli.get_api_key()
    captured = capsys.readouterr()
    assert result is None
    assert "vk_live_" in captured.err
    assert "anonymous tier" in captured.err


def test_api_key_format_warning_silenced_by_quiet(capsys, monkeypatch):
    monkeypatch.setenv("VIVORY_API_KEY", "garbage_token_no_prefix")
    monkeypatch.setenv("VIVORY_MCP_QUIET", "1")
    cli._format_warned = False
    cli.get_api_key()
    captured = capsys.readouterr()
    assert captured.err == ""


def test_api_key_valid_prefix_passes_through(monkeypatch):
    monkeypatch.setenv("VIVORY_API_KEY", "vk_live_aaaaaaaaaaaaaaaa")
    cli._format_warned = False
    assert cli.get_api_key() == "vk_live_aaaaaaaaaaaaaaaa"
    monkeypatch.setenv("VIVORY_API_KEY", "vk_test_bbbbbbbbbbbbbbbb")
    cli._format_warned = False
    assert cli.get_api_key() == "vk_test_bbbbbbbbbbbbbbbb"


def test_quiet_banner_env(capsys, monkeypatch):
    monkeypatch.setenv("VIVORY_MCP_QUIET", "1")
    srv._startup_banner()
    captured = capsys.readouterr()
    assert captured.err == ""


def test_banner_emits_by_default(capsys, monkeypatch):
    monkeypatch.delenv("VIVORY_MCP_QUIET", raising=False)
    monkeypatch.delenv("VIVORY_API_KEY", raising=False)
    srv._startup_banner()
    captured = capsys.readouterr()
    assert "vivory-mcp-verification" in captured.err
    assert "101 tools" in captured.err


def test_client_request_supports_not_found_ok():
    """request() exposes not_found_ok param (default True for verification)."""
    import inspect
    sig = inspect.signature(cli.request)
    assert "not_found_ok" in sig.parameters
    # Default = True (verification gateway semantics — 404 is data, not error)
    assert sig.parameters["not_found_ok"].default is True


def test_client_api_key_strip(monkeypatch):
    # 0.11.0: valid-prefix keys are returned trimmed; whitespace-only is None.
    monkeypatch.setenv("VIVORY_API_KEY", "  vk_live_padded_key  ")
    cli._format_warned = False
    assert cli.get_api_key() == "vk_live_padded_key"
    monkeypatch.setenv("VIVORY_API_KEY", "   ")
    cli._format_warned = False
    assert cli.get_api_key() is None


def test_peer_review_phase_a_routing():
    """v0.9.0 Phase A expansion — 3 new peer-review tools route to gateway."""
    bulk = srv.HANDLERS["bulk_peer_review_lookup"]({"article_ids": ["1", "2"]})
    assert bulk == ("POST", "verify/peer-review/bulk", None, {"article_ids": ["1", "2"]})

    registry = srv.HANDLERS["reviewer_registry"]({})
    assert registry == ("GET", "verify/peer-review/reviewers", None, None)

    stats_all = srv.HANDLERS["peer_review_stats"]({})
    assert stats_all == ("GET", "verify/peer-review/stats", {"service": None}, None)

    stats_life = srv.HANDLERS["peer_review_stats"]({"service": "life"})
    assert stats_life == ("GET", "verify/peer-review/stats", {"service": "life"}, None)


def test_peer_review_cluster_has_5_tools():
    """Peer-review cluster grew 2 → 5 in v0.9.0 (Phase A of Peer Review MCP planning)."""
    expected = {
        "verify_peer_review",
        "persona_verdict_lookup",
        "bulk_peer_review_lookup",
        "reviewer_registry",
        "peer_review_stats",
    }
    names = {t.name for t in srv.TOOLS}
    missing = expected - names
    assert not missing, f"Peer-review cluster missing tools: {missing}"


def test_provenance_phase_a_cluster_has_13_tools():
    """v0.10.0 Phase A — provenance cluster expanded 4 → 13.

    Adds standards-backed who/when/where/what verification across image/
    video/PDF: EXIF + perceptual hash + video ffprobe + frame hash + PDF
    metadata + file hash + CID v1 + AI generator signature + combined
    summary + RFC 3161 timestamp wrapper. All zero-new-deps.
    """
    expected = {
        # Phase 0 (pre-existing)
        "verify_c2pa",
        "verify_pdf_provenance",
        "verify_hash_chain",
        "detect_watermark",
        # Phase A (2026-05-21)
        "verify_timestamp_rfc3161",
        "extract_image_exif",
        "image_perceptual_hash",
        "extract_video_metadata",
        "video_frame_hash_sample",
        "extract_pdf_metadata",
        "compute_file_hash",
        "ai_generator_signature_lookup",
        "provenance_summary",
    }
    names = {t.name for t in srv.TOOLS}
    missing = expected - names
    assert not missing, f"Provenance Phase A missing tools: {missing}"


def test_provenance_phase_a_routing():
    """All 9 new Phase A provenance tools route to /verify/* gateway paths."""
    # EXIF
    out = srv.HANDLERS["extract_image_exif"]({"image_url": "https://x/img.jpg"})
    assert out == ("POST", "verify/exif", None, {"image_url": "https://x/img.jpg"})

    # Perceptual hash with default size
    out = srv.HANDLERS["image_perceptual_hash"]({"image_url": "https://x/img.jpg"})
    method, path, _, body = out
    assert method == "POST" and path == "verify/perceptual-hash"
    assert body["size"] == 8
    assert body["compare_dhash"] is None and body["compare_ahash"] is None

    # Perceptual hash with compare
    out = srv.HANDLERS["image_perceptual_hash"]({
        "image_url": "https://x/img.jpg",
        "size": 16,
        "compare_dhash": "deadbeefcafebabe1234567890abcdef",
    })
    body = out[3]
    assert body["size"] == 16
    assert body["compare_dhash"] == "deadbeefcafebabe1234567890abcdef"

    # Video metadata
    out = srv.HANDLERS["extract_video_metadata"]({"video_url": "https://x/v.mp4"})
    assert out == ("POST", "verify/video-metadata", None, {"video_url": "https://x/v.mp4"})

    # Video frame hash sample with default count
    out = srv.HANDLERS["video_frame_hash_sample"]({"video_url": "https://x/v.mp4"})
    assert out[3]["sample_count"] == 5

    # PDF metadata
    out = srv.HANDLERS["extract_pdf_metadata"]({"pdf_url": "https://x/doc.pdf"})
    assert out == ("POST", "verify/pdf-metadata", None, {"pdf_url": "https://x/doc.pdf"})

    # File hash
    out = srv.HANDLERS["compute_file_hash"]({"file_url": "https://x/anything"})
    assert out == ("POST", "verify/file-hash", None, {"file_url": "https://x/anything"})

    # AI generator signature lookup
    out = srv.HANDLERS["ai_generator_signature_lookup"]({"image_url": "https://x/img.png"})
    assert out == ("POST", "verify/ai-generator-signature", None, {"image_url": "https://x/img.png"})

    # Provenance summary
    out = srv.HANDLERS["provenance_summary"]({"file_url": "https://x/anything", "mime_hint": "image/jpeg"})
    assert out == ("POST", "verify/provenance-summary", None, {"file_url": "https://x/anything", "mime_hint": "image/jpeg"})

    # RFC 3161 timestamp wrapper
    digest = "a" * 64
    out = srv.HANDLERS["verify_timestamp_rfc3161"]({"digest_hex": digest})
    assert out == ("POST", "verify/timestamp", None, {"digest_hex": digest, "digest_algorithm": "sha256"})

    # Case-insensitive normalize on digest_hex
    digest_upper = "B" * 64
    out = srv.HANDLERS["verify_timestamp_rfc3161"]({"digest_hex": digest_upper})
    assert out[3]["digest_hex"] == "b" * 64


# ---------------------------------------------------------------------------
# Helpers


def _placeholder_args(schema: dict) -> dict:
    args = {}
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    any_of = schema.get("anyOf", [])
    if any_of and not required:
        first = any_of[0]
        required = set(first.get("required", []))
    for key in required:
        spec = props.get(key, {})
        t = spec.get("type", "string")
        if t == "string":
            pat = spec.get("pattern")
            if pat in (r"^\d{5}$", "^[0-9]{5}$"):
                args[key] = "11680"
            elif pat in (r"^\d{6}$", "^[0-9]{6}$"):
                args[key] = "202604"
            else:
                args[key] = spec.get("default") or "placeholder"
        elif t == "integer":
            args[key] = spec.get("default") or 1
        elif t == "number":
            args[key] = spec.get("default") or 1.0
        elif t == "boolean":
            args[key] = spec.get("default", True)
        elif t == "array":
            args[key] = []
        else:
            args[key] = None
    return args
