"""Sanity tests for vivory-mcp-korea.

Runs offline (no httpx/network). Verifies:
- every tool has a valid JSON Schema inputSchema
- every tool name is matched by a handler
- handler returns (path, params) tuple shape
- server error envelope has stable code field
- banner respects VIVORY_MCP_QUIET=1

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

from vivory_mcp_korea import server as srv  # noqa: E402
from vivory_mcp_korea import client as cli  # noqa: E402


def test_tool_count_matches_version_claim():
    """v0.4.0 claims 55 tools across 15 sources."""
    assert len(srv.TOOLS) == 55, f"Expected 55 tools, got {len(srv.TOOLS)}"


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
    """Every inputSchema must be a valid JSON Schema (draft-07 compatible)."""
    schema = tool.inputSchema
    assert isinstance(schema, dict), f"{tool.name} has non-dict schema"
    assert schema.get("type") == "object", f"{tool.name} schema is not type=object"
    # Validate the schema document itself (meta-validation)
    jsonschema.Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize("tool", srv.TOOLS, ids=lambda t: t.name)
def test_handler_returns_path_params_tuple(tool):
    """Every handler returns (path: str, params: dict) when called with empty args."""
    handler = srv.HANDLERS[tool.name]
    # Some tools have required params; build placeholder args from schema
    args = _placeholder_args(tool.inputSchema)
    result = handler(args)
    assert isinstance(result, tuple) and len(result) == 2, (
        f"{tool.name} handler did not return (path, params)"
    )
    path, params = result
    assert isinstance(path, str) and path, f"{tool.name} returned empty path"
    assert params is None or isinstance(params, dict), f"{tool.name} params not dict"


def test_error_envelope_unknown_tool():
    """Unknown tool returns structured JSON envelope, not a bare string."""
    out = asyncio.run(srv.call_tool("definitely_not_a_real_tool_xyz", {}))
    assert len(out) == 1
    payload = json.loads(out[0].text)
    assert payload["code"] == "UNKNOWN_TOOL"
    assert payload["tool"] == "definitely_not_a_real_tool_xyz"
    assert payload["gateway"] == "vivory-mcp-korea"
    assert "error" in payload


def test_error_classification():
    """Known error types map to stable codes."""
    assert srv._classify_error(RuntimeError("rate limit exceeded")) == "RATE_LIMIT"
    assert srv._classify_error(RuntimeError("API key rejected")) == "AUTH"
    assert srv._classify_error(TimeoutError("timed out")) == "TIMEOUT"
    assert srv._classify_error(ValueError("bad arg")) == "VALIDATION"
    assert srv._classify_error(RuntimeError("upstream 500")) == "UPSTREAM"


def test_quiet_banner_env(capsys, monkeypatch):
    """VIVORY_MCP_QUIET=1 silences startup banner."""
    monkeypatch.setenv("VIVORY_MCP_QUIET", "1")
    srv._startup_banner()
    captured = capsys.readouterr()
    assert captured.err == "", "Banner emitted despite VIVORY_MCP_QUIET=1"


def test_banner_emits_by_default(capsys, monkeypatch):
    monkeypatch.delenv("VIVORY_MCP_QUIET", raising=False)
    monkeypatch.delenv("VIVORY_API_KEY", raising=False)
    srv._startup_banner()
    captured = capsys.readouterr()
    assert "vivory-mcp-korea" in captured.err
    assert "55 tools" in captured.err


def test_client_get_api_base_default():
    assert cli.get_api_base() == "https://api.vivory.app/api"


def test_client_get_api_base_override(monkeypatch):
    monkeypatch.setenv("VIVORY_API_BASE", "http://localhost:8000/api/")
    assert cli.get_api_base() == "http://localhost:8000/api"


def test_client_api_key_strip(monkeypatch):
    monkeypatch.setenv("VIVORY_API_KEY", "  test-key  ")
    assert cli.get_api_key() == "test-key"
    monkeypatch.setenv("VIVORY_API_KEY", "   ")
    assert cli.get_api_key() is None


def test_client_get_signature_has_not_found_ok():
    """client.get accepts not_found_ok for parity with verification gateway."""
    import inspect
    sig = inspect.signature(cli.get)
    assert "not_found_ok" in sig.parameters


# ---------------------------------------------------------------------------
# Helpers


def _placeholder_args(schema: dict) -> dict:
    """Build minimal valid args from inputSchema (required-only, placeholder values)."""
    args = {}
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    # Also honor anyOf required clauses (pick first)
    any_of = schema.get("anyOf", [])
    if any_of and not required:
        first = any_of[0]
        required = set(first.get("required", []))
    for key in required:
        spec = props.get(key, {})
        t = spec.get("type", "string")
        if t == "string":
            # Use pattern-aware placeholder if possible
            pat = spec.get("pattern")
            if pat == r"^\d{5}$" or pat == "^[0-9]{5}$":
                args[key] = "11680"
            elif pat == r"^\d{6}$" or pat == "^[0-9]{6}$":
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
