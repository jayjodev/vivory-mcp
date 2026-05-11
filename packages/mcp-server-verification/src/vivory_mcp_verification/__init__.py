"""Vivory umbrella MCP server for verifiable AI work.

Aggregates verification tools under a single MCP server name
(`vivory-verification`). v0.1 ships 7 tool categories:

- Claim       — extract / verify / archive citations from arbitrary text
- DOI         — resolve, retraction-check, author network
- Archive     — Wayback / archive.today snapshot lookup + capture
- Repro       — Vivory Repro Hub hash registry lookup + diff
- Provenance  — C2PA, PDF metadata, hash chain, watermark detect
- Peer review — Vivory Research peer-review verdict lookup
- Forecast    — Vivory forecast track record (crypto.vivory.app/forecast) + agent submit

All tools are HTTP wrappers over `api.vivory.app/api/verify/*` and
adjacent endpoints. The backend handles caching, attribution, and
upstream auth. The MCP layer translates LLM tool calls into HTTP GETs.
"""

__version__ = "0.1.0"
