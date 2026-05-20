"""PyPI package supply-chain verification.

Sister of `npm` — same heuristics applied to Python packages:

- `verify_pypi_package` — fetch pypi.org/pypi/{name}/json + flag yanked
  releases, deprecation classifier, age, last-release recency, maintainer
  email match (single-author profile == elevated risk).
- `verify_pypi_typosquat` — given a candidate name, surface popular PyPI
  packages within edit-distance 2 + risk score. Mirrors the npm tool's
  contract so agents can use both behind one branch.

Backed by /api/verify/pypi/* on api.vivory.app. Upstream = pypi.org JSON
API (public, no key). Vivory caches + adds typosquat heuristic.
"""
from __future__ import annotations

from typing import Callable

from mcp.types import Tool

_PYPI_NAME = {
    "type": "string",
    "minLength": 1,
    "maxLength": 214,
    "pattern": r"^[A-Za-z0-9][A-Za-z0-9._-]*$",
    "description": (
        "PyPI package name. PEP 503 normalization applied server-side "
        "(case-insensitive, '._-' collapsed)."
    ),
}

TOOLS: list[Tool] = [
    Tool(
        name="verify_pypi_package",
        description=(
            "Fetch a single PyPI package's JSON record and return a verdict "
            "envelope: latest version, yanked releases list, deprecation "
            "classifier from trove tags, maintainer count, last-release "
            "recency (days since), risk flags (recent_first_release, "
            "single_maintainer, yanked_latest, dev_only_classifier). Use "
            "before pip-installing or citing a package as a dependency. "
            "Returns 404-envelope when name is unknown."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": _PYPI_NAME,
                "version": {
                    "type": "string",
                    "maxLength": 64,
                    "description": (
                        "Optional specific version (PEP 440, e.g. '1.2.3'). "
                        "If omitted, returns latest release's metadata."
                    ),
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="verify_pypi_typosquat",
        description=(
            "Detect possible PyPI typosquat candidates for a given name. "
            "Compares against a curated list of top-downloaded PyPI packages "
            "via Damerau-Levenshtein edit distance ≤ 2. For each near-match, "
            "returns the popular package's monthly downloads (PyPI Stats), "
            "your candidate's age, and a heuristic risk score 0~100. Score "
            "> 60 = candidate name is suspiciously close to a popular package "
            "and was first-released recently with low downloads. Use before "
            "pip-installing an unfamiliar package."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": _PYPI_NAME,
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    ),
]


HANDLERS: dict[str, Callable[[dict], tuple[str, str, dict | None, dict | None]]] = {
    "verify_pypi_package": lambda a: (
        "GET",
        "verify/pypi/package",
        {"name": a.get("name"), "version": a.get("version")},
        None,
    ),
    "verify_pypi_typosquat": lambda a: (
        "GET",
        "verify/pypi/typosquat",
        {"name": a.get("name")},
        None,
    ),
}
