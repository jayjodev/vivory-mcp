"""Per-source tool definitions for the umbrella MCP server.

Each module exports:
- `TOOLS`: list[mcp.types.Tool]
- `HANDLERS`: dict[str, Callable[[dict], tuple[str, dict]]]
  (tool_name → (api_path, query_params))
"""
