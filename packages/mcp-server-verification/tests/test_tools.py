"""Sanity tests for vivory-mcp-verification.

Runs offline (no httpx/network). Mirrors korea test suite — verifies:
- 45 tool count
- every tool has handler returning (method, path, params, body) tuple
- inputSchema is valid JSON Schema
- error envelope is structured JSON with stable code field
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
    """v0.4.0 claims 45 tools across 18 categories."""
    assert len(srv.TOOLS) == 45, f"Expected 45 tools, got {len(srv.TOOLS)}"


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


def test_error_classification():
    assert srv._classify_error(RuntimeError("rate limit exceeded")) == "RATE_LIMIT"
    assert srv._classify_error(RuntimeError("API key rejected")) == "AUTH"
    assert srv._classify_error(TimeoutError("timed out")) == "TIMEOUT"
    assert srv._classify_error(ValueError("bad arg")) == "VALIDATION"
    assert srv._classify_error(RuntimeError("upstream 500")) == "UPSTREAM"


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
    assert "45 tools" in captured.err


def test_client_request_supports_not_found_ok():
    """request() exposes not_found_ok param (default True for verification)."""
    import inspect
    sig = inspect.signature(cli.request)
    assert "not_found_ok" in sig.parameters
    # Default = True (verification gateway semantics — 404 is data, not error)
    assert sig.parameters["not_found_ok"].default is True


def test_client_api_key_strip(monkeypatch):
    monkeypatch.setenv("VIVORY_API_KEY", "  test-key  ")
    assert cli.get_api_key() == "test-key"
    monkeypatch.setenv("VIVORY_API_KEY", "   ")
    assert cli.get_api_key() is None


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
