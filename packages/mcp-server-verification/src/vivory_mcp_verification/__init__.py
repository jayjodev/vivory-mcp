"""Vivory umbrella MCP server for verifiable AI work.

Aggregates verification tools under a single MCP server name
(`vivory-verification`). v0.6 ships 68 tools across 27 categories.

See `vivory_mcp_verification.server` module docstring for the full
cluster list. All tools are HTTP wrappers over `api.vivory.app/api/verify/*`
and adjacent endpoints (`/api/blockchain-audit/*`). The backend handles
caching, attribution, and upstream auth. The MCP layer translates LLM
tool calls into HTTP GETs/POSTs.

Tier:
- Anonymous           — 100/day per IP, no signup
- Tools Pro bridge    — $4.99/mo, 1,000 calls/month (use Tools Pro key)
- Vivory API Pro      — $29/mo USDC, 10,000/day, no auto-renew, no custody
                        Same key unlocks sibling `vivory-mcp-korea` (124 total tools)
"""

__version__ = "0.6.0"
