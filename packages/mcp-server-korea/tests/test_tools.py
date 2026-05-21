"""Sanity tests for vivory-mcp-korea v0.6.0 — DEPRECATION RELEASE.

v0.6.0 은 deprecation marker package 다. 단일 `vivory_korea_deprecated_
migration_notice` tool 만 노출하고, 어떤 호출이든 migration payload (status:
deprecated, replacement_package: vivory-mcp-verification) 를 반환한다. 모든
raw 한국 데이터 wrapper 는 제거 — Korean 출처는 vivory-mcp-verification 의
verdict (kor_law_currency, kor_company_status, doi_retraction_status) 안에서
underlying evidence 로 사용된다.

Run: `pytest -q` from package root.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

import jsonschema

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vivory_mcp_korea import server as srv  # noqa: E402
import vivory_mcp_korea  # noqa: E402


def test_version_is_deprecation_release():
    """v0.6.0 = deprecation final release."""
    assert vivory_mcp_korea.__version__ == "0.6.0"


def test_tools_reduced_to_deprecation_notice():
    """Deprecation release exposes exactly 1 tool — the migration notice."""
    assert len(srv.TOOLS) == 1, (
        f"Deprecation release should have exactly 1 tool, got {len(srv.TOOLS)}"
    )
    assert srv.TOOLS[0].name == "vivory_korea_deprecated_migration_notice"


def test_deprecation_tool_schema_valid():
    """Deprecation tool's inputSchema is a valid JSON Schema (empty object)."""
    schema = srv.TOOLS[0].inputSchema
    assert isinstance(schema, dict)
    assert schema.get("type") == "object"
    jsonschema.Draft202012Validator.check_schema(schema)


def test_handler_registered_for_deprecation_tool():
    """Tools and handlers in 1-to-1 correspondence."""
    tool_names = {t.name for t in srv.TOOLS}
    handler_names = set(srv.HANDLERS.keys())
    assert tool_names == handler_names, (
        f"Mismatch: tools={tool_names} handlers={handler_names}"
    )


def test_deprecation_tool_call_returns_migration_payload():
    """Calling the deprecation tool returns the migration notice payload."""
    out = asyncio.run(srv.call_tool("vivory_korea_deprecated_migration_notice", {}))
    assert len(out) == 1
    payload = json.loads(out[0].text)
    assert payload["status"] == "deprecated"
    assert payload["replacement_package"] == "vivory-mcp-verification"
    assert payload["install_command"] == "uvx vivory-mcp-verification"
    assert "korean_verdict_tools_in_verification" in payload
    assert "kor_law_currency" in payload["korean_verdict_tools_in_verification"]
    assert "kor_company_status" in payload["korean_verdict_tools_in_verification"]
    assert "doi_retraction_status" in payload["korean_verdict_tools_in_verification"]


def test_removed_v0_5_tool_returns_deprecation_signal():
    """Any v0.5 tool name (e.g. kosis_population) now returns deprecation
    payload — silent break X, migration signal preserved."""
    out = asyncio.run(srv.call_tool("kosis_population", {}))
    assert len(out) == 1
    payload = json.loads(out[0].text)
    assert payload["status"] == "deprecated"
    assert payload["code"] == "DEPRECATED"
    assert payload["removed_tool_called"] == "kosis_population"
    assert payload["replacement_package"] == "vivory-mcp-verification"
    assert payload["gateway"] == "vivory-mcp-korea (deprecated)"


def test_unknown_tool_also_returns_deprecation_signal():
    """Even tool names that never existed return deprecation — entire
    package is deprecated regardless of called name."""
    out = asyncio.run(srv.call_tool("definitely_not_a_real_tool_xyz", {}))
    payload = json.loads(out[0].text)
    assert payload["status"] == "deprecated"
    assert payload["code"] == "DEPRECATED"


def test_banner_announces_deprecation_by_default(capsys, monkeypatch):
    """Loud deprecation banner — first thing existing v0.5 users see."""
    monkeypatch.delenv("VIVORY_MCP_QUIET", raising=False)
    srv._startup_banner()
    captured = capsys.readouterr()
    assert "vivory-mcp-korea" in captured.err
    assert "DEPRECATED" in captured.err
    assert "vivory-mcp-verification" in captured.err


def test_quiet_banner_env(capsys, monkeypatch):
    """VIVORY_MCP_QUIET=1 silences the deprecation banner."""
    monkeypatch.setenv("VIVORY_MCP_QUIET", "1")
    srv._startup_banner()
    captured = capsys.readouterr()
    assert captured.err == "", "Banner emitted despite VIVORY_MCP_QUIET=1"
