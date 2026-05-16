"""Sanity tests for vivory-mcp-kosis (DEPRECATED, EOL 2026-12-31).

Final maintenance tests. Verifies tool count + schema + Bearer fwd-compat.
Mirrors korea/verification test suites but lighter (this package is frozen).

Run: `pytest -q` from package root.
"""
from __future__ import annotations

import os
import sys

import jsonschema
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vivory_mcp_kosis import server as srv  # noqa: E402
from vivory_mcp_kosis import client as cli  # noqa: E402


def test_tool_count():
    """Final frozen surface = 15 KOSIS tools."""
    assert len(srv.TOOLS) == 15, f"Expected 15 tools, got {len(srv.TOOLS)}"


# Note: kosis legacy uses inline dispatch inside call_tool(), no module-level
# HANDLERS registry, so we skip handler-coverage assertion. Schema + Bearer
# + anyOf coverage below is sufficient for the EOL maintenance bar.


@pytest.mark.parametrize("tool", srv.TOOLS, ids=lambda t: t.name)
def test_input_schema_is_valid_json_schema(tool):
    schema = tool.inputSchema
    assert isinstance(schema, dict), f"{tool.name} has non-dict schema"
    assert schema.get("type") == "object"
    jsonschema.Draft202012Validator.check_schema(schema)


def test_table_explanation_has_anyof():
    """kosis_table_explanation must declare anyOf (stat_id OR org_id+tbl_id)."""
    tool = next(t for t in srv.TOOLS if t.name == "kosis_table_explanation")
    schema = tool.inputSchema
    assert "anyOf" in schema, "kosis_table_explanation missing anyOf constraint"
    clauses = schema["anyOf"]
    assert any(c.get("required") == ["stat_id"] for c in clauses)
    assert any(set(c.get("required", [])) == {"org_id", "tbl_id"} for c in clauses)


def test_client_get_api_base_default():
    assert cli.get_api_base() == "https://api.vivory.app/api"


def test_client_bearer_fwd_compat(monkeypatch):
    """v0.1.2 adds VIVORY_API_KEY Bearer support for migration parity."""
    monkeypatch.setenv("VIVORY_API_KEY", "test-fwd-compat-key")
    headers = cli._build_headers()
    assert headers.get("Authorization") == "Bearer test-fwd-compat-key"


def test_client_no_bearer_when_key_absent(monkeypatch):
    monkeypatch.delenv("VIVORY_API_KEY", raising=False)
    headers = cli._build_headers()
    assert "Authorization" not in headers
