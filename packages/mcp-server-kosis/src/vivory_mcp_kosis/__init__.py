"""Vivory MCP server for KOSIS (Statistics Korea).

DEPRECATED v0.1.4 — both this package AND the intermediate
`vivory-mcp-korea` umbrella are retired. Migrate directly to
`vivory-mcp-verification` (Korean verdict tools included, same Pro key).

Any tool call returns the deprecation payload. The upstream KOSIS
gateway at api.vivory.app/api/public-tools/kosis/* went cluster-internal
on 2026-05-22, so old proxying would 404 regardless of this MCP layer.
"""

__version__ = "0.1.4"
