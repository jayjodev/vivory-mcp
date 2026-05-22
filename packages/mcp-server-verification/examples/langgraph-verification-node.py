"""LangGraph verification node — Vivory MCP wrapper as a drop-in graph step.

Usage:

    from langgraph.graph import StateGraph
    from vivory_verification_node import (
        VerificationState,
        extract_artifacts,
        verify_artifacts,
        gate_publish,
    )

    graph = StateGraph(VerificationState)
    graph.add_node("extract", extract_artifacts)
    graph.add_node("verify", verify_artifacts)
    graph.add_node("gate", gate_publish)

    graph.add_edge("extract", "verify")
    graph.add_edge("verify", "gate")

    # Plug `gate` into your generation graph as the publication boundary.
    # If state["verdict"] == "block", route back to your generation node
    # with state["block_reasons"] as the corrective signal.

This module talks to api.vivory.app/api/verify/* directly via httpx,
so it works whether or not you've registered the MCP. (The MCP and
the REST gateway expose the same surface; the MCP is for agents that
want one-line install + structured tool descriptions, the REST is for
programmatic pipelines.)

License: MIT.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Literal, TypedDict

import httpx

VIVORY_BASE = os.environ.get("VIVORY_API_BASE", "https://api.vivory.app/api")
VIVORY_KEY = os.environ.get("VIVORY_API_KEY")  # optional; anonymous = 100/day/IP

DOI_RE = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s)>\]]+", re.IGNORECASE)
LEI_RE = re.compile(r"\b([A-Z0-9]{20})\b")
QID_RE = re.compile(r"\bQ\d+\b")


class VerificationState(TypedDict, total=False):
    """LangGraph state passed between nodes.

    Required input: `content` — the text about to be published.
    Output: `verdict`, `block_reasons`, `warnings`, `passed`, `sources`.
    """

    content: str
    artifacts: dict[str, list[str]]
    results: list[dict]
    verdict: Literal["pass", "warn", "block"]
    block_reasons: list[str]
    warnings: list[str]
    passed: list[str]
    sources: list[str]


@dataclass
class _GatewayClient:
    base: str = VIVORY_BASE
    key: str | None = VIVORY_KEY
    timeout: float = 10.0

    def __post_init__(self):
        headers = {"Accept": "application/json"}
        if self.key:
            headers["Authorization"] = f"Bearer {self.key}"
        self._client = httpx.Client(headers=headers, timeout=self.timeout)

    def get(self, path: str, **params) -> dict:
        try:
            r = self._client.get(f"{self.base}/{path.lstrip('/')}", params=params)
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            return {
                "implementation_phase": "error",
                "error": str(exc),
                "data": None,
            }


# ────────────────────────────────────────────────────────────────────
# Node 1 — extract checkable artifacts from arbitrary text
# ────────────────────────────────────────────────────────────────────

def extract_artifacts(state: VerificationState) -> VerificationState:
    content = state.get("content", "")
    artifacts: dict[str, list[str]] = {
        "dois": list(set(DOI_RE.findall(content))),
        "urls": list(set(URL_RE.findall(content))),
        "leis": list(set(LEI_RE.findall(content))),
        "qids": list(set(QID_RE.findall(content))),
    }
    # filter LEIs (20-char alphanumeric) out of DOIs (which share characters)
    artifacts["leis"] = [
        lei for lei in artifacts["leis"]
        if not any(lei in doi for doi in artifacts["dois"])
    ]
    return {**state, "artifacts": artifacts}


# ────────────────────────────────────────────────────────────────────
# Node 2 — call the Vivory gateway for each artifact
# ────────────────────────────────────────────────────────────────────

def verify_artifacts(state: VerificationState) -> VerificationState:
    gw = _GatewayClient()
    results: list[dict] = []
    sources: set[str] = set()

    for doi in state.get("artifacts", {}).get("dois", []):
        meta = gw.get("verify/doi", doi=doi)
        retr = gw.get("verify/doi/retraction", doi=doi)
        results.append({"kind": "doi", "id": doi, "meta": meta, "retraction": retr})
        sources.update(meta.get("sources") or [])
        sources.update(retr.get("sources") or [])

    for url in state.get("artifacts", {}).get("urls", []):
        arch = gw.get("verify/archive/check", url=url)
        results.append({"kind": "url", "id": url, "archive": arch})
        sources.update(arch.get("sources") or [])

    for lei in state.get("artifacts", {}).get("leis", []):
        e = gw.get("verify/entity/lei", lei=lei)
        results.append({"kind": "lei", "id": lei, "entity": e})
        sources.update(e.get("sources") or [])

    for qid in state.get("artifacts", {}).get("qids", []):
        q = gw.get("verify/wikidata", qid=qid)
        results.append({"kind": "qid", "id": qid, "wikidata": q})
        sources.update(q.get("sources") or [])

    return {**state, "results": results, "sources": sorted(sources)}


# ────────────────────────────────────────────────────────────────────
# Node 3 — aggregate results into a verdict (pass | warn | block)
# ────────────────────────────────────────────────────────────────────

def gate_publish(state: VerificationState) -> VerificationState:
    block: list[str] = []
    warn: list[str] = []
    passed: list[str] = []

    for r in state.get("results", []):
        if r["kind"] == "doi":
            meta = r["meta"].get("data") or {}
            retr = r["retraction"].get("data") or {}
            if r["meta"].get("implementation_phase") == "error":
                warn.append(f"DOI {r['id']}: gateway error — treat as unverified.")
                continue
            if not meta.get("title"):
                block.append(f"DOI {r['id']} does not resolve in Crossref/OpenAlex.")
            elif retr.get("retracted"):
                date = retr.get("retraction_date", "unknown date")
                block.append(f"DOI {r['id']} was RETRACTED on {date}.")
            else:
                passed.append(f"DOI {r['id']} ({meta.get('year')})")

        elif r["kind"] == "url":
            arch = r["archive"].get("data") or {}
            if r["archive"].get("implementation_phase") == "error":
                warn.append(f"URL {r['id']}: archive check failed.")
                continue
            if not arch.get("snapshot_count", 0):
                warn.append(f"URL {r['id']} has no Wayback snapshot. Consider capturing.")
            else:
                passed.append(f"URL {r['id']} ({arch.get('snapshot_count')} snapshots)")

        elif r["kind"] == "lei":
            ent = r["entity"].get("data") or {}
            status = ent.get("status")
            if status != "ACTIVE":
                block.append(f"LEI {r['id']} status = {status or 'NOT FOUND'} (expected ACTIVE).")
            else:
                passed.append(f"LEI {r['id']} → {ent.get('legal_name')}")

        elif r["kind"] == "qid":
            q = r["wikidata"].get("data") or {}
            if not q.get("label"):
                block.append(f"Wikidata {r['id']} does not exist.")
            else:
                passed.append(f"{r['id']} → {q.get('label')}")

    verdict: Literal["pass", "warn", "block"]
    if block:
        verdict = "block"
    elif warn:
        verdict = "warn"
    else:
        verdict = "pass"

    return {
        **state,
        "verdict": verdict,
        "block_reasons": block,
        "warnings": warn,
        "passed": passed,
    }


# ────────────────────────────────────────────────────────────────────
# CLI smoke test
# ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = """
    AlphaFold (10.1038/s41586-021-03819-2) achieved state-of-the-art accuracy.
    See also the Vivory project (https://vivory.app) and the GLEIF lookup
    for Apple Inc. (HWUPKR0MPOU8FGXBT394). Wikidata Q42 is Douglas Adams.
    """
    state: VerificationState = {"content": sample}
    state = extract_artifacts(state)
    state = verify_artifacts(state)
    state = gate_publish(state)

    print(f"VERDICT: {state['verdict']}")
    print(f"  passed:   {len(state['passed'])}")
    print(f"  warnings: {len(state['warnings'])}")
    print(f"  blocks:   {len(state['block_reasons'])}")
    print(f"  sources:  {state['sources']}")
    for line in state["block_reasons"]:
        print(f"  ❌ {line}")
    for line in state["warnings"]:
        print(f"  ⚠️  {line}")
    for line in state["passed"]:
        print(f"  ✅ {line}")
