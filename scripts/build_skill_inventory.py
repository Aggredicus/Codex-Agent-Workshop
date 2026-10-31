"""Generate an allowlisted public inventory of repository skills, never of people.

No network access, environment variables, Git metadata, user profiles, arbitrary
document text, private files or secrets are read. This is NOT a competence test.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INV = ROOT / "skill-inventory"
DEST = INV / "inventory.json"
SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
PII = re.compile(
    r"(?:[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|"
    r"github_pat_[a-z0-9_]{15,}|gh[pousr]_[a-z0-9_]{20,}|"
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b|\b\+?\d{1,3}[\s-]\d{3}[\s-]\d{3}[\s-]\d{4}\b)",
    re.I,
)


def read_safe(path: Path, *, max_bytes: int = 130_000) -> str:
    rel = path.relative_to(ROOT)
    node = ROOT
    for segment in rel.parts:
        node /= segment
        if node.is_symlink():
            raise ValueError("Symlink not allowed in inventory input")
    if not path.is_file() or path.stat().st_size > max_bytes:
        raise ValueError("Input unavailable or exceeds size limit")
    return path.read_text(encoding="utf-8")


def taxonomy() -> tuple[list[dict], dict[str, list[str]]]:
    cfg = json.loads(read_safe(INV / "taxonomy.json"))
    if cfg.get("schema_version") != 1:
        raise ValueError("Unsupported taxonomy schema")
    categories = cfg["categories"]
    mapping = cfg["source_skill_map"]
    ids: set[str] = set()
    if len(categories) > 500 or len(mapping) > 250:
        raise ValueError("Taxonomy too large")
    for item in categories:
        cid, label, category = (item[k] for k in ("id", "label", "category"))
        if not all(isinstance(x, str) for x in (cid, label, category)):
            raise ValueError("Invalid taxonomy entry")
        if not SLUG.fullmatch(cid) or not SLUG.fullmatch(category) or cid in ids:
            raise ValueError("Duplicate or unsafe capability ID")
        if not label or len(label) > 75 or PII.search(label):
            raise ValueError("Unsafe public label")
        ids.add(cid)
    for name, values in mapping.items():
        if not SLUG.fullmatch(name) or not isinstance(values, list) or not values:
            raise ValueError("Invalid source skill")
        if any(not isinstance(v, str) or v not in ids for v in values):
            raise ValueError("Source refers to unknown capability")
    return categories, mapping


def declared_skill(path: Path) -> str | None:
    raw = read_safe(path, max_bytes=65_536)
    lines = raw.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:40]:
        if line.strip() == "---":
            break
        match = re.fullmatch(r"name:\s*([a-z][a-z0-9-]*)\s*", line)
        if match and SLUG.fullmatch(match.group(1)):
            return match.group(1)
    return None


def build_inventory() -> dict:
    categories, mapping = taxonomy()
    documented: set[str] = set()
    for name in sorted(mapping):
        path = ROOT / ".agents" / "skills" / name / "SKILL.md"
        if path.exists() and declared_skill(path) == name:
            documented.add(name)
    references = {skill: 0 for skill in documented}
    team_dir = ROOT / "teams"
    if team_dir.is_dir() and not team_dir.is_symlink():
        paths = sorted(team_dir.glob("*/team.toml"))
        if len(paths) > 100:
            raise ValueError("Too many team manifests")
        for path in paths:
            if not SLUG.fullmatch(path.parent.name):
                continue
            parsed = tomllib.loads(read_safe(path))
            roles = parsed.get("roles", [])
            if not isinstance(roles, list) or len(roles) > 100:
                raise ValueError("Invalid team roles")
            for role in roles:
                for name in role.get("skills", []):
                    if isinstance(name, str) and name in references:
                        references[name] += 1
    capabilities = []
    for item in categories:
        present = sorted(name for name in documented if item["id"] in mapping[name])
        capabilities.append({
            "id": item["id"],
            "label": item["label"],
            "category": item["category"],
            "evidence_status": "documented-in-repository" if present else "not-observed",
            "repository_skill_ids": present,
            "team_role_references": sum(references[name] for name in present),
        })
    data = {
        "schema_version": 1,
        "subject": "repository-artifacts-only",
        "no_person_or_agent_competence_claims": True,
        "sources": [".agents/skills/*/SKILL.md", "teams/*/team.toml"],
        "scanned_skill_assets": sorted(documented),
        "capabilities": capabilities,
        "privacy": "No identities, raw descriptions, paths to user data, contact details, credentials or private assignments",
        "unknown_meaning": "not-observed is not proof that a person or agent lacks the skill",
    }
    encoded = json.dumps(data, ensure_ascii=False, sort_keys=True)
    if len(encoded) > 400_000 or PII.search(encoded):
        raise ValueError("Rejected potentially sensitive public output")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    group.add_argument("--stdout", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(build_inventory(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.stdout:
        print(encoded, end="")
        return 0
    if args.write:
        if DEST.is_symlink():
            raise ValueError("Output symlink forbidden")
        DEST.write_text(encoded, encoding="utf-8")
        print("Updated skill-inventory/inventory.json")
        return 0
    if not DEST.exists() or read_safe(DEST, max_bytes=400_000) != encoded:
        print("Skill inventory is stale; regenerate with --write", file=sys.stderr)
        return 1
    print("Skill inventory is current and privacy-scoped")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError, UnicodeError, json.JSONDecodeError) as error:
        print("Skill inventory build failed; source details withheld for privacy", file=sys.stderr)
        raise SystemExit(1)
