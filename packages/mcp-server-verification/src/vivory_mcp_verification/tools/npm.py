"""npm package supply-chain verification.

Two tools for vetting npm dependencies before an agent installs / cites them:

- `verify_npm_package` — fetch registry metadata + flag deprecation, yank,
  age, maintainer count, last-publish recency. Returns a verdict envelope
  agents can branch on.
- `verify_npm_typosquat` — given a candidate name, search the registry for
  popular packages within edit-distance 1~2 that the candidate might be
  squatting. Returns risk score + closest legit matches.

Backed by /api/verify/npm/* on api.vivory.app. Upstream = registry.npmjs.org
(public, no key). Vivory adds the typosquat heuristic + caching.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_NPM_NAME = {
    "type": "string",
    "minLength": 1,
    "maxLength": 214,
    "pattern": r"^(@[a-z0-9][a-z0-9._-]*/)?[a-z0-9][a-z0-9._-]*$",
    "description": (
        "npm package name. Scoped (@org/pkg) or bare (pkg). Lowercase, "
        "URL-safe. Validated against npm's naming rules."
    ),
}

TOOLS: list[Tool] = [
    Tool(
        name="verify_npm_package",
        description=(
            "Fetch a single npm package's registry record and return a "
            "verdict envelope: latest version, deprecation/yank state, "
            "maintainer count, last-publish recency (days since), download "
            "trend (last week vs last month), and risk flags (recent_first_"
            "publish, single_maintainer, deprecated, yanked_versions_exist). "
            "Use before an agent npm-installs or cites a package as a "
            "dependency. Returns 404-envelope when name is unknown."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": _NPM_NAME,
                "version": {
                    "type": "string",
                    "maxLength": 64,
                    "description": (
                        "Optional specific version (semver, e.g. '1.2.3'). "
                        "If omitted, returns latest tag's metadata."
                    ),
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="verify_npm_typosquat",
        description=(
            "Detect possible npm typosquat candidates for a given name. "
            "Compares against a curated list of top-downloaded npm packages "
            "via Damerau-Levenshtein edit distance ≤ 2. For each near-match, "
            "returns the popular package's monthly download count, your "
            "candidate's age, and a heuristic risk score 0~100. Score > 60 "
            "means the candidate name is suspiciously close to a popular "
            "package and was published recently with low downloads — classic "
            "typosquat profile. Use before installing an unfamiliar package."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": _NPM_NAME,
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_npm_package": lambda a: (
        "GET",
        "verify/npm/package",
        {"name": a.get("name"), "version": a.get("version")},
        None,
    ),
    "verify_npm_typosquat": lambda a: (
        "GET",
        "verify/npm/typosquat",
        {"name": a.get("name")},
        None,
    ),
}
