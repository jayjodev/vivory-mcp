"""Vivory umbrella MCP server for verifiable AI work.

Aggregates verification tools under a single MCP server name
(`vivory-verification`). v0.10.0 ships 98 tools across 36 categories —
provenance cluster expanded 4→13 (Phase A standards-backed who/when/
where/what verification across image/video/PDF: EXIF + perceptual hash
+ video ffprobe + video frame hash + PDF metadata + file hash + CID v1
+ AI generator signature lookup + combined provenance summary + RFC
3161 timestamp wrapper). All Phase A tools are standards-only — no ML
inference, no new Python deps, no new system binaries beyond
ffmpeg/ffprobe. Honest about scope: signature match only, absence of
match does NOT prove human-created.

See `vivory_mcp_verification.server` module docstring for the full
cluster list. All tools are HTTP wrappers over `api.vivory.app/api/verify/*`
and adjacent endpoints (`/api/blockchain-audit/*`). The backend handles
caching, attribution, and upstream auth. The MCP layer translates LLM
tool calls into HTTP GETs/POSTs.

Tier:
- Anonymous           — 100/day per IP, no signup
- Tools Pro bridge    — $4.99/mo, 1,000 calls/month (use Tools Pro key)
- Vivory API Pro      — $29/mo USDC, 10,000/day, no auto-renew, no custody
                        Same key unlocks sibling Korea verification primitives
"""

__version__ = "0.10.0"
