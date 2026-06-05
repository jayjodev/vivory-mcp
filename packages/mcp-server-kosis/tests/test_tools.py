"""Sanity tests for vivory-mcp-kosis (DEPRECATED, EOL 2026-12-31).

Final maintenance tests for the frozen deprecation release. The package was
gutted to a single migration-notice tool (the `client` module + the 15-tool
KOSIS surface were removed); these tests assert the deprecation shape.

Run: `pytest -q` from package root.
"""
from __future__ import annotations

import os
import sys

import jsonschema
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import vivory_mcp_kosis  # noqa: E402
from vivory_mcp_kosis import server as srv  # noqa: E402


def test_version_is_deprecation_release():
    """v0.1.x = deprecation maintenance line."""
    assert vivory_mcp_kosis.__version__ == "0.1.4"


def test_tools_reduced_to_deprecation_notice():
    """Deprecation release exposes exactly 1 tool — the migration notice."""
    assert len(srv.TOOLS) == 1, f"Deprecation release should have exactly 1 tool, got {len(srv.TOOLS)}"
    assert srv.TOOLS[0].name == "vivory_kosis_deprecated_migration_notice"


@pytest.mark.parametrize("tool", srv.TOOLS, ids=lambda t: t.name)
def test_input_schema_is_valid_json_schema(tool):
    schema = tool.inputSchema
    assert isinstance(schema, dict), f"{tool.name} has non-dict schema"
    assert schema.get("type") == "object"
    jsonschema.Draft202012Validator.check_schema(schema)
