"""Korean apartment real-transaction verification (MOLIT RTMS).

Vivory's Korean public-data moat exposed for fact-checking apartment market
claims. Source = 국토교통부 (Ministry of Land, Infrastructure and Transport)
RTMS API, ingested into Vivory DB daily via nationwide sweep
(`apt_trade_tx` + `apt_rent_tx` × ~250 sigungu).

Backed by /api/verify/apt/snapshot + /api/verify/apt/price.

Sister of `filing` (SEC EDGAR — US filings) and `entity` (GLEIF LEI). Korean
citizens / overseas investors / apartment-comp researchers / agents writing
real-estate copy can verify any claimed transaction price against the
authoritative MOLIT registry.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="apt_market_snapshot",
        description=(
            "Korean apartment market snapshot for a single 시군구 (sigungu) × "
            "month × tx type, from MOLIT RTMS. Returns: n transactions, mean / "
            "median / p25 / p75 / min / max prices in 만원 (10k KRW), cancellation "
            "count, mean exclusive area (m²). For rent, separates jeonse "
            "(deposit-only) from wolse (monthly rent) and reports deposit + "
            "monthly statistics. Use to ground statements like 'average Gangnam "
            "apartment trade in April 2026 was X'. lawd_cd is the 5-digit "
            "법정동 prefix (e.g. '11680'=강남구, '41135'=성남시 분당구). Data "
            "is reported with 30~60 day delay, so most recent month is "
            "underreported — prefer month-1 for reliable numbers."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "lawd_cd": {
                    "type": "string",
                    "pattern": "^[0-9]{5}$",
                    "description": "5-digit 법정동 sigungu prefix (e.g. '11680').",
                },
                "deal_ymd": {
                    "type": "string",
                    "pattern": "^[0-9]{6}$",
                    "description": "Deal month, YYYYMM (e.g. '202604').",
                },
                "tx_type": {
                    "type": "string",
                    "enum": ["trade", "rent"],
                    "default": "trade",
                    "description": "trade = 매매 (sale), rent = 전월세 (lease).",
                },
                "exclude_canceled": {
                    "type": "boolean",
                    "default": True,
                    "description": "Exclude canceled (해제) transactions from price stats. trade only.",
                },
            },
            "required": ["lawd_cd", "deal_ymd"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="verify_apt_price",
        description=(
            "Verify a specific Korean apartment transaction-price claim against "
            "MOLIT RTMS. Filter by sigungu × month × (optional) apt name × "
            "(optional) ±10% area band, then check whether `claim_amount_manwon` "
            "(for trade) or `claim_deposit_manwon` + `claim_monthly_manwon` (for "
            "rent) matches an actual recorded transaction. Returns up to 20 "
            "matching candidates plus a verdict: exact_match, in_range, "
            "percentile within candidates, diff vs median (% and 만원). Use this "
            "before publishing or asserting a specific apartment price — "
            "hallucinated comps are common in LLM real-estate output."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "lawd_cd": {
                    "type": "string",
                    "pattern": "^[0-9]{5}$",
                    "description": "5-digit 법정동 sigungu prefix.",
                },
                "deal_ymd": {
                    "type": "string",
                    "pattern": "^[0-9]{6}$",
                    "description": "Deal month, YYYYMM.",
                },
                "apt_name": {
                    "type": "string",
                    "maxLength": 200,
                    "description": "Apartment complex name (partial match, ILIKE).",
                },
                "exclusive_area": {
                    "type": "number",
                    "minimum": 10,
                    "maximum": 500,
                    "description": "Exclusive area in m² (전용면적). Filter ±10%.",
                },
                "claim_amount_manwon": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Claimed sale price in 만원 (10k KRW). trade only.",
                },
                "claim_deposit_manwon": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Claimed deposit in 만원. rent only.",
                },
                "claim_monthly_manwon": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Claimed monthly rent in 만원 (0 for jeonse). rent only.",
                },
                "tx_type": {
                    "type": "string",
                    "enum": ["trade", "rent"],
                    "default": "trade",
                },
            },
            "required": ["lawd_cd", "deal_ymd"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "apt_market_snapshot": lambda a: (
        "GET",
        "verify/apt/snapshot",
        {
            "lawd_cd": a.get("lawd_cd"),
            "deal_ymd": a.get("deal_ymd"),
            "tx_type": a.get("tx_type", "trade"),
            "exclude_canceled": a.get("exclude_canceled", True),
        },
        None,
    ),
    "verify_apt_price": lambda a: (
        "GET",
        "verify/apt/price",
        {
            "lawd_cd": a.get("lawd_cd"),
            "deal_ymd": a.get("deal_ymd"),
            "apt_name": a.get("apt_name"),
            "exclusive_area": a.get("exclusive_area"),
            "claim_amount_manwon": a.get("claim_amount_manwon"),
            "claim_deposit_manwon": a.get("claim_deposit_manwon"),
            "claim_monthly_manwon": a.get("claim_monthly_manwon"),
            "tx_type": a.get("tx_type", "trade"),
        },
        None,
    ),
}
