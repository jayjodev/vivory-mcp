"""Sanity tests for vivory-mcp-verification.

Runs offline (no httpx/network). Mirrors korea test suite — verifies:
- 13 tool count (v0.14.0 moat collapse 2026-06-05: 4 clusters —
  law·reconcile·doi·provenance — dropping ~74 commodity + surface-internal
  tools; agent surface = the Vivory-only moat, web Tools keep breadth)
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
    """v0.14.0 claims 13 tools across 4 categories (moat collapse 2026-06-05)."""
    assert len(srv.TOOLS) == 13, f"Expected 13 tools, got {len(srv.TOOLS)}"


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
    assert "13 tools" in captured.err


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


def test_moat_cluster_membership():
    """v0.14.0 moat collapse — exactly 13 tools across 4 moat clusters."""
    expected = {
        # law (5) — Korean public-data moat
        "kor_law_lookup", "kor_law_currency", "kor_case_search",
        "kor_bill_status", "kor_company_status",
        # reconcile (3) — deterministic-provenance-hash cross-source engine
        "company_reconcile", "recall_reconcile", "person_reconcile",
        # doi (2) — research-integrity anchor
        "verify_doi", "doi_retraction_check",
        # provenance (3) — offline-verifiable receipt backbone
        "verify_c2pa", "verify_hash_chain", "compute_file_hash",
    }
    names = {t.name for t in srv.TOOLS}
    assert names == expected, f"moat drift: missing={expected - names} extra={names - expected}"


def test_retired_clusters_are_gone():
    """Commodity + surface-internal clusters retired in v0.14.0 must not reappear."""
    names = {t.name for t in srv.TOOLS}
    retired = {
        # surface-internal
        "verify_peer_review", "bulk_peer_review_lookup", "reviewer_registry",
        "peer_review_stats", "persona_verdict_lookup",
        "verify_repro_hash", "repro_hub_lookup", "repro_artifact_diff",
        "forecast_ensemble", "forecast_calibration",
        # commodity public-API wrappers (sample)
        "verify_lei", "verify_quake", "verify_indicator", "verify_protocol_tvl",
        "verify_qid", "verify_trial", "verify_filing", "verify_orcid",
        "sanctions_screen", "verify_archive", "verify_npm_package",
    }
    leaked = retired & names
    assert not leaked, f"Retired tools still present: {leaked}"


def test_provenance_receipt_cluster_has_3_tools():
    """v0.14.0 — provenance trimmed to the offline-verifiable receipt backbone."""
    expected = {"verify_c2pa", "verify_hash_chain", "compute_file_hash"}
    names = {t.name for t in srv.TOOLS}
    missing = expected - names
    assert not missing, f"Receipt backbone missing tools: {missing}"


def test_receipt_routing():
    """Receipt backbone tools route to /verify/* gateway paths."""
    out = srv.HANDLERS["verify_c2pa"]({"image_url": "https://x/img.jpg"})
    assert out == ("POST", "verify/c2pa", None, {"image_url": "https://x/img.jpg"})

    out = srv.HANDLERS["compute_file_hash"]({"file_url": "https://x/anything"})
    assert out == ("POST", "verify/file-hash", None, {"file_url": "https://x/anything"})

    out = srv.HANDLERS["verify_hash_chain"]({"items": [{"content": "a", "hash": "h"}]})
    method, path, _, body = out
    assert method == "POST" and path == "verify/hash-chain"
    assert body["algorithm"] == "sha256"


def test_doi_anchor_routing():
    """Research-integrity anchor — verdict + retraction gate."""
    assert srv.HANDLERS["verify_doi"]({"doi": "10.1/x"}) == ("GET", "verify/doi", {"doi": "10.1/x"}, None)
    assert srv.HANDLERS["doi_retraction_check"]({"doi": "10.1/x"}) == ("GET", "verify/doi/retraction", {"doi": "10.1/x"}, None)


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
