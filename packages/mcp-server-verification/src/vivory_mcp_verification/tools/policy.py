"""Custom verification policy framework.

For agents whose verification needs don't match the built-in workflow
packs, this cluster exposes a generic policy evaluator. A policy is a JSON
spec listing ordered verification steps (each step = one underlying
gateway endpoint + args + a pass condition). The gateway runs them in
order, short-circuits on `fail_fast`, and returns a per-step + aggregate
report.

This is the lowest-level composition primitive in the verification MCP —
agents can build their own workflow packs without server changes.

- `policy_list_presets` — returns 3 built-in presets (paper_repro, crypto_
  diligence, ai_output_verify) as ready-to-evaluate policy specs. Useful
  starting points; agents can clone + customize.
- `policy_evaluate` — runs a policy spec end-to-end and returns the report.

Backed by /api/verify/policy/* on api.vivory.app.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_POLICY_STEP_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 64,
            "description": "Step label (free-form, used in report).",
        },
        "endpoint": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200,
            "description": (
                "Gateway endpoint path under /api/verify/* (e.g. "
                "'doi', 'doi/retraction', 'archive/check'). Must be "
                "in the allowlist returned by `policy_list_presets`."
            ),
        },
        "method": {
            "type": "string",
            "enum": ["GET", "POST"],
            "default": "GET",
        },
        "params": {
            "type": "object",
            "description": "Query params for GET, or JSON body for POST.",
            "additionalProperties": True,
        },
        "pass_if": {
            "type": "object",
            "description": (
                "Pass condition. Currently supported: "
                "{'field': 'data.status', 'in': ['active']} (path-based "
                "value check). Omit to mark step as informational-only."
            ),
            "additionalProperties": True,
        },
        "on_fail": {
            "type": "string",
            "enum": ["stop", "continue", "warn"],
            "default": "continue",
            "description": (
                "stop = abort policy with overall_verdict=fail; "
                "warn = mark step as warning but continue; "
                "continue = mark fail but keep evaluating."
            ),
        },
    },
    "required": ["name", "endpoint"],
    "additionalProperties": False,
}

TOOLS: list[Tool] = [
    Tool(
        name="policy_list_presets",
        description=(
            "List built-in verification policy presets. Each preset returns "
            "a ready-to-evaluate policy spec (same shape `policy_evaluate` "
            "accepts) — agents can use them as-is or clone + customize. "
            "Also returns the allowlist of endpoint paths a policy may "
            "reference (security boundary — policies cannot call arbitrary "
            "URLs, only the verification gateway). Use this once at "
            "agent-init time, then call `policy_evaluate` with the chosen "
            "spec for each input."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    ),
    Tool(
        name="policy_evaluate",
        description=(
            "Evaluate a custom verification policy spec against an input. "
            "The spec is an ordered list of steps; each step calls one "
            "/api/verify/* endpoint with the given params and applies an "
            "optional pass condition. Returns per-step verdict (pass / "
            "warn / fail / skipped) + aggregate `overall_verdict` ∈ "
            "{pass, warn, fail}. `on_fail='stop'` short-circuits on first "
            "failure. Use to build agent-specific verification gates "
            "without needing a workflow pack PR to Vivory."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "policy_name": {
                    "type": "string",
                    "maxLength": 128,
                    "description": "Free-form label for the report.",
                },
                "steps": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 20,
                    "items": _POLICY_STEP_SCHEMA,
                },
                "fail_fast": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "If True, stop at the first step with verdict=fail "
                        "regardless of its on_fail setting."
                    ),
                },
            },
            "required": ["steps"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "policy_list_presets": lambda a: (
        "GET",
        "verify/policy/presets",
        None,
        None,
    ),
    "policy_evaluate": lambda a: (
        "POST",
        "verify/policy/evaluate",
        None,
        {
            "policy_name": a.get("policy_name"),
            "steps": a.get("steps"),
            "fail_fast": a.get("fail_fast", False),
        },
    ),
}
