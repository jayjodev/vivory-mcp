"""vivory-mcp-verification, discontinued.

The hosted API this package wrapped (api.vivory.app) was shut down on
2026-08-09. Versions up to 0.14.0 fail on every call because that address
only redirects to the vivory.app home page. 0.15.0 is the final release: it
keeps the entry point so existing MCP client configs start cleanly, and its
only tool tells the agent that the service has ended. No network calls.
"""

__version__ = "0.15.0"
