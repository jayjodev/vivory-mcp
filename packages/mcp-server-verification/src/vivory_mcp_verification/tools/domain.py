"""Domain reputation — RDAP whois + DoH DNS lookup.

Two pillars of "does this domain look legit before I trust what it says":

- `verify_domain_whois` — RDAP-based registrar + registration age +
  expiration date. RDAP is the modern, JSON-based successor to legacy
  whois — works for most gTLDs and many ccTLDs without an API key.
- `verify_domain_dns` — DNS A/AAAA/MX/TXT/NS/CAA records via Cloudflare
  DoH (DNS-over-HTTPS). Lets an agent check SPF/DMARC TXT records,
  MX deliverability, and CAA pinning before quoting a domain.

Backed by /api/verify/domain/* on api.vivory.app. No upstream API key.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_DOMAIN = {
    "type": "string",
    "minLength": 4,
    "maxLength": 253,
    "description": (
        "Bare domain (no scheme) — 'example.com' or 'sub.example.co.uk'. "
        "Schemes/paths are stripped automatically. Punycode TLDs accepted."
    ),
}

TOOLS: list[Tool] = [
    Tool(
        name="verify_domain_whois",
        description=(
            "RDAP whois lookup for a domain — registrar, status flags "
            "(clientTransferProhibited, etc.), creation/expiration/last-"
            "changed dates, nameservers, and a computed age_days field. "
            "Use to flag suspiciously new domains (age_days < 30 is a "
            "common phishing heuristic) or domains expiring soon. Empty "
            "events typically means the TLD's RDAP server is uncooperative "
            "— fall back to verify_archive on the domain's website for "
            "proof-of-existence evidence."
        ),
        inputSchema={
            "type": "object",
            "properties": {"domain": _DOMAIN},
            "required": ["domain"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="verify_domain_dns",
        description=(
            "DNS record lookup via Cloudflare DoH JSON API. Returns each "
            "requested record type with TTL + raw RDATA. Common uses: "
            "(a) read SPF/DMARC from TXT before flagging an email as "
            "spoofed, (b) confirm MX records exist before trusting an "
            "email domain, (c) read CAA pinning to know which CAs are "
            "authorized to issue certs for the domain. Default types "
            "A,AAAA,MX,TXT,NS — pass `types` to override."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "domain": _DOMAIN,
                "types": {
                    "type": "string",
                    "maxLength": 200,
                    "description": (
                        "Comma-separated record types from {A,AAAA,MX,TXT,"
                        "NS,CAA,SOA}. Defaults to 'A,AAAA,MX,TXT,NS'."
                    ),
                },
            },
            "required": ["domain"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_domain_whois": lambda a: (
        "GET",
        "verify/domain/whois",
        {"domain": a.get("domain")},
        None,
    ),
    "verify_domain_dns": lambda a: (
        "GET",
        "verify/domain/dns",
        {"domain": a.get("domain"), "types": a.get("types")},
        None,
    ),
}
