"""Vivory umbrella MCP server for verifiable AI work.

Aggregates verification tools under a single MCP server name
(`vivory-verification`). v0.9.0 ships 89 tools across 36 categories —
peer-review cluster expanded 2→5 (bulk_peer_review_lookup,
reviewer_registry, peer_review_stats) per Phase A of the Peer Review
MCP planning doc. Reviewer panels (Life/Crypto persona pools) and the
aggregation rule are now publicly addressable — Trust pillar legibility
for the 1% audience that wants to see the review trail.

See `vivory_mcp_verification.server` module docstring for the full
cluster list. All tools are HTTP wrappers over `api.vivory.app/api/verify/*`
and adjacent endpoints (`/api/blockchain-audit/*`). The backend handles
caching, attribution, and upstream auth. The MCP layer translates LLM
tool calls into HTTP GETs/POSTs.

Tier:
- Anonymous           — 100/day per IP, no signup
- Tools Pro bridge    — $4.99/mo, 1,000 calls/month (use Tools Pro key)
- Vivory API Pro      — $29/mo USDC, 10,000/day, no auto-renew, no custody
                        Same key unlocks sibling `vivory-mcp-korea` (145 total tools)
"""

__version__ = "0.9.0"
