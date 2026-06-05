"""vivory-mcp-korea — DEPRECATED as of v0.6.0.

This package is deprecated. **Install vivory-mcp-verification instead.**

    uvx vivory-mcp-verification

Why deprecated
==============
Korea raw-data wrappers conflicted with Vivory's mission of *verifiable AI
work*. Vivory's value is verifying claims, not redistributing data. The
verification MCP now uses Korean sources (법령정보센터, NTS, DART, KMA,
KOSIS, etc.) as *underlying evidence* for verdicts — consistent with both
the mission and each source's terms of service.

Migration
=========
Korean verdict tools already in verification MCP (v0.9.0+):
  - kor_law_currency       — 한국 법령 현행여부 verdict (law.go.kr)
  - kor_company_status     — KYB cross-verification (NTS + CSL)
  - doi_retraction_status  — DOI retraction (Crossref + OpenAlex + PubPeer)

Future Korean verdict candidates (added based on demand signal):
  - macro-claim verdict (KOSIS + BOK)
  - listed-company health verdict (DART)
  - weather-claim verdict (KMA)
  - etc.

Tools Pro $4.99/mo key authenticates vivory-mcp-verification after the
2026-06-01 bundle absorb (single paid tier; prior standalone $29/mo Pro
tier retired). No new functionality will ship in vivory-mcp-korea — this
release contains only a migration notice tool. v0.6.1 = squat-lock reclaim
after v0.6.0 hard-delete.
v0.6.2 = wheel cleanup (deleted unused raw-wrapper source modules that
were retired in v0.6.0 but still bundled; ToS-incompatible source code
should not ship even if unreachable at runtime).
"""

__version__ = "0.6.2"
