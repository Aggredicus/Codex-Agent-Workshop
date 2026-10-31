"""Local pseudonymous node registry. No hardware fingerprinting or public identity.

IDs are random UUIDs for a person, a computer installation, or an agent instance.
This is a local bookkeeping tool, NOT identity proof or an access-control service.
GitHub permissions and signed/trusted approvals must enforce consequential actions.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import secrets
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "skill-inventory" / "private"
REGISTRY = PRIVATE / "nodes.json"
NODE_KINDS = {"person", "computer", "agent"}
SLUG = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,79}$")
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
ID = re.compile(r"^(person|computer|agent)_[0-9a-f]{32}$")


def _fresh_id(kind: str) -> str:
    if kind not in NODE_KINDS:
        raise ValueError("Unknown node type")
    return f"{kind}_{uuid.uuid4().hex}"


def _safe_parent() -> None:
    base = ROOT / "skill-inventory"
    if base.is_symlink() or PRIVATE.is_symlink() or REGISTRY.is_symlink():
        raise ValueError("Refusing symlinked node registry")
    PRIVATE.mkdir(mode=0o700, exist_ok=True)
    if os.name == "posix":
        PRIVATE.chmod(0o700)


def _read() -> dict:
    _safe_parent()
    if not REGISTRY.exists():
        return {"schema_version": 1, "nodes": {}}
    if REGISTRY.stat().st_size > 2_000_000:
        raise ValueError("Registry too large")
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("nodes"), dict):
        raise ValueError("Invalid private node registry")
    return data


def _write(data: dict) -> None:
    _safe_parent()
    # Atomic replace to avoid corrupting the registry on a failed write.
    fd, name = tempfile.mkstemp(prefix=".nodes-", dir=PRIVATE)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fp:
            json.dump(data, fp, sort_keys=True, indent=2)
            fp.write("\n")
            fp.flush()
            os.fsync(fp.fileno())
        if os.name == "posix":
            os.chmod(name, 0o600)
        os.replace(name, REGISTRY)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _manifest(source: str, version: str, digest: str) -> dict:
    if not SLUG.fullmatch(source) or not VERSION.fullmatch(version) or not DIGEST.fullmatch(digest):
        raise ValueError("Use a public slug for source, bounded version and sha256 artifact digest")
    return {"source_id": source, "version": version, "artifact_digest": digest}


def _same_agent(current: dict, new: dict) -> bool:
    return all(current.get(key) == new[key] for key in ("source_id", "version", "artifact_digest"))


def enroll(kind: str, *, operator: str | None = None, computer: str | None = None,
           source: str | None = None, version: str | None = None,
           digest: str | None = None) -> str:
    data = _read()
    if kind not in NODE_KINDS:
        raise ValueError("Invalid node type")
    node = {"kind": kind, "inventory": [], "privileges": [],
            "review_state": "pending", "identity_assurance": "self-registered"}
    if kind == "agent":
        if not operator or not computer or not (source and version and digest):
            raise ValueError("Agent needs existing person and computer nodes plus source/version/digest")
        if data["nodes"].get(operator, {}).get("kind") != "person":
            raise ValueError("Operator must be an enrolled person")
        if data["nodes"].get(computer, {}).get("kind") != "computer":
            raise ValueError("Computer must be an enrolled computer")
        node["operator_id"] = operator
        node["computer_id"] = computer
        node["origin"] = _manifest(source, version, digest)
        node["origin_assurance"] = "declared-unverified"
    elif any(x is not None for x in (operator, computer, source, version, digest)):
        raise ValueError("Only agent nodes accept origin/binding arguments")
    node_id = _fresh_id(kind)
    while node_id in data["nodes"]:
        node_id = _fresh_id(kind)
    data["nodes"][node_id] = node
    _write(data)
    return node_id


def upgrade(agent_id: str, source: str, version: str, digest: str) -> dict:
    data = _read()
    if not ID.fullmatch(agent_id) or data["nodes"].get(agent_id, {}).get("kind") != "agent":
        raise ValueError("Unknown agent node")
    node = data["nodes"][agent_id]
    new = _manifest(source, version, digest)
    changed = not _same_agent(node["origin"], new)
    if changed:
        node["origin"] = new
        node["origin_assurance"] = "declared-unverified"
        node["inventory"] = []
        node["privileges"] = []
        node["review_state"] = "pending"
        node["capability_reassessment_required"] = True
        _write(data)
    return {
        "node_id": agent_id,
        "origin_changed": changed,
        "capability_reassessment_required": changed or node.get("capability_reassessment_required", False),
        "privileges": [],  # Never expose or infer effective grants.
        "decision": "deny-until-trusted-reassessment",
    }


def inventory_for(node_id: str, skill_ids: list[str], *, taxonomy_ids: set[str]) -> dict:
    data = _read()
    if not ID.fullmatch(node_id) or node_id not in data["nodes"]:
        raise ValueError("Unknown node")
    if any(not isinstance(x, str) or x not in taxonomy_ids for x in skill_ids):
        raise ValueError("Unrecognized capability ID")
    node = data["nodes"][node_id]
    node["inventory"] = sorted(set(skill_ids))
    node["review_state"] = "pending"
    node["privileges"] = []
    _write(data)
    return {"node_id": node_id, "capabilities_recorded": len(node["inventory"]),
            "effective_privileges": 0, "review_state": "pending"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    register = sub.add_parser("enroll", help="Create a new local anonymous node")
    register.add_argument("--kind", choices=sorted(NODE_KINDS), required=True)
    for name in ("operator", "computer", "source", "version", "digest"):
        register.add_argument("--" + name)
    change = sub.add_parser("upgrade", help="Record agent origin change; invalidate capabilities/grants")
    change.add_argument("--id", required=True)
    for name in ("source", "version", "digest"):
        change.add_argument("--" + name, required=True)
    inv = sub.add_parser("inventory", help="Record self-declared node capabilities (no grants)")
    inv.add_argument("--id", required=True)
    inv.add_argument("--skill", action="append", default=[])
    sub.add_parser("summary", help="Show counts, never IDs or private node data")
    args = ap.parse_args()
    if args.command == "enroll":
        print(enroll(args.kind, operator=args.operator, computer=args.computer,
                     source=args.source, version=args.version, digest=args.digest))
    elif args.command == "upgrade":
        print(json.dumps(upgrade(args.id, args.source, args.version, args.digest), sort_keys=True))
    elif args.command == "inventory":
        from build_skill_inventory import taxonomy
        categories, _ = taxonomy()
        print(json.dumps(inventory_for(args.id, args.skill,
                                       taxonomy_ids={x["id"] for x in categories}), sort_keys=True))
    elif args.command == "summary":
        data = _read()
        print(json.dumps({"node_counts": {kind: sum(1 for n in data["nodes"].values()
            if n["kind"] == kind) for kind in sorted(NODE_KINDS)},
            "private": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        # Avoid echoing potentially sensitive data in exceptions.
        print("Node registry action rejected; no public data was written", file=sys.stderr)
        raise SystemExit(1)
