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

Same $29/mo Pro key works for vivory-mcp-verification. No new functionality
will ship in vivory-mcp-korea — this v0.6.0 release contains only a
migration notice tool.
"""

__version__ = "0.6.0"
