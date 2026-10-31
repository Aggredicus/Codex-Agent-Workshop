#!/usr/bin/env python3
"""Validate/synchronize the three canonical offline gateway catalogs.

By default this is a read-only quality gate. Use --write intentionally to
refresh JSON snapshots embedded in docs/volunteer/index.html.
No network access, package installation or GitHub token is required.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "docs" / "volunteer"
PAGE = DIRECTORY / "index.html"
SOURCES = {
    "catalog": DIRECTORY / "opportunities.json",
    "offered-catalog": DIRECTORY / "offered-skills.json",
    "verified-tasks": DIRECTORY / "open-tasks.json",
}


def _script_pattern(identifier: str) -> re.Pattern[str]:
    return re.compile(
        r'(?P<start><script type="application/json" id="'
        + re.escape(identifier)
        + r'">\s*)(?P<body>.*?)(?P<end>\s*</script>)',
        re.DOTALL,
    )


def _unique(items: list[dict], key: str, category: str) -> None:
    vals = [item[key] for item in items]
    if len(vals) != len(set(vals)):
        raise ValueError(f"Duplicate {category} {key}")


def _github_url(raw: str, *, issue: bool = False) -> None:
    url = urlsplit(raw)
    if url.scheme != "https" or url.netloc != "github.com":
        raise ValueError("Untrusted repository/issue URL")
    parts = url.path.strip("/").split("/")
    if len(parts) < 2 or parts[0] != "Aggredicus" or not parts[1]:
        raise ValueError("Unexpected GitHub repository owner")
    if issue and not (len(parts) == 4 and parts[2] == "issues" and parts[3].isdigit()):
        raise ValueError("Expected a direct GitHub issue URL")
    if url.query or url.fragment or url.username or url.password:
        raise ValueError("Unexpected URL parameters")


def _validate(data: dict[str, dict]) -> None:
    incoming, outgoing, tasks = (data[k] for k in ("catalog", "offered-catalog", "verified-tasks"))
    assert incoming["version"] == 1
    skills = incoming["skills"]
    _unique(skills, "id", "skill")
    ids = {x["id"] for x in skills}
    _unique(incoming["opportunities"], "id", "candidate")
    _unique(outgoing["offerings"], "id", "offering")
    _unique(tasks["tasks"], "id", "task")

    for opp in incoming["opportunities"]:
        if opp["status"] != "candidate" or not opp["skills"] or not set(opp["skills"]) <= ids:
            raise ValueError(f"Unverified or invalid candidate: {opp['id']}")
        _github_url(opp["url"])

    if outgoing["publication_state"] != "proposed":
        raise ValueError("Assistance claims cannot be auto-promoted")
    for offer in outgoing["offerings"]:
        if not offer["skills"] or not set(offer["skills"]) <= ids:
            raise ValueError(f"Unknown assistance skills: {offer['id']}")
        if offer["request_scope"] != "public-source":
            raise ValueError("Unreviewed request scope")
        _github_url(offer["evidence_repository"])

    for task in tasks["tasks"]:
        _github_url(task["url"], issue=True)
        if task["status_at_verification"] != "open":
            raise ValueError("Non-open issue in the verified snapshot")
        if not task["skills"] or not set(task["skills"]) <= ids:
            raise ValueError("Unknown task skill")
        if int(task["url"].rsplit("/", 1)[-1]) != task["issue_number"]:
            raise ValueError("Task issue number does not match URL")


def check_or_write(write: bool = False) -> int:
    data = {key: json.loads(path.read_text(encoding="utf-8")) for key, path in SOURCES.items()}
    _validate(data)
    html = PAGE.read_text(encoding="utf-8")
    changed = []
    for identifier, canonical in data.items():
        pattern = _script_pattern(identifier)
        matches = list(pattern.finditer(html))
        if len(matches) != 1:
            raise ValueError(f"Expected one embedded JSON block: {identifier}")
        current = json.loads(matches[0].group("body"))
        if current != canonical:
            changed.append(identifier)
        if write:
            payload = json.dumps(canonical, ensure_ascii=False, separators=(",", ":")).replace("<", r"\u003c")
            html = pattern.sub(
                lambda m: m.group("start") + payload + m.group("end"),
                html,
                count=1,
            )
    if write:
        PAGE.write_text(html, encoding="utf-8")
        print("Embedded snapshots synchronized")
        return 0
    if changed:
        print("Out-of-sync embedded catalogs: " + ", ".join(changed), file=sys.stderr)
        print("Run: python scripts/sync_gateway_catalogs.py --write", file=sys.stderr)
        return 1
    print("Gateway catalog validation passed")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Refresh embedded offline JSON snapshots")
    args = parser.parse_args()
    try:
        raise SystemExit(check_or_write(write=args.write))
    except (KeyError, ValueError, AssertionError, TypeError, json.JSONDecodeError) as exc:
        print(f"Invalid contributor gateway catalog: {exc}", file=sys.stderr)
        raise SystemExit(1)
