"""Tool catalog for the Vivory Verification MCP server.

Each module exports two top-level names:

- ``TOOLS``      : list[Tool]  — MCP Tool definitions surfaced to the LLM
- ``HANDLERS``   : dict[str, Callable[[dict], tuple[str, str, dict|None, dict|None]]]
                   keyed by tool name, returning (method, path, params, body)
                   for ``client.request`` to dispatch.
"""
