"""Local SQLite state for pseudonymous humans, computers, and agent instances.

No server, accounts, hardware fingerprints or third-party packages required.
A local registry is NOT an authorization service; GitHub's authenticated
permissions and protected-branch review enforce real repository actions.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sqlite3
import uuid
from typing import Iterator

SLUG = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,79}$")
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
NODE_ID = re.compile(r"^(human|computer|agent)_[0-9a-f]{32}$")
KINDS = {"human", "computer", "agent"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS registry_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS nodes (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL CHECK(kind IN ('human','computer','agent')),
  operator_id TEXT REFERENCES nodes(id),
  computer_id TEXT REFERENCES nodes(id),
  origin_source TEXT,
  origin_version TEXT,
  origin_digest TEXT,
  origin_assurance TEXT NOT NULL DEFAULT 'unverified',
  review_state TEXT NOT NULL DEFAULT 'pending',
  created_utc TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_nodes_kind ON nodes(kind);
CREATE INDEX IF NOT EXISTS idx_nodes_operator ON nodes(operator_id);
CREATE TABLE IF NOT EXISTS node_skills (
  node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  skill_id TEXT NOT NULL,
  evidence_state TEXT NOT NULL CHECK(evidence_state IN ('self-declared','repo-documented')),
  PRIMARY KEY(node_id,skill_id)
);
CREATE INDEX IF NOT EXISTS idx_node_skills_skill ON node_skills(skill_id);
CREATE TABLE IF NOT EXISTS grant_proposals (
  proposal_id TEXT PRIMARY KEY,
  node_id TEXT NOT NULL REFERENCES nodes(id),
  skill_id TEXT NOT NULL,
  action TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'pending' CHECK(state IN ('pending','invalidated','declined')),
  created_utc TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_proposals_node_state ON grant_proposals(node_id,state);
CREATE TABLE IF NOT EXISTS agent_versions (
  version_id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent_id TEXT NOT NULL REFERENCES nodes(id),
  source TEXT NOT NULL,
  version TEXT NOT NULL,
  digest TEXT NOT NULL,
  recorded_utc TEXT NOT NULL,
  reason TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS event_log (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  node_id TEXT REFERENCES nodes(id),
  kind TEXT NOT NULL,
  detail_json TEXT NOT NULL,
  created_utc TEXT NOT NULL
);
"""

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def origin(source: str, version: str, digest: str) -> tuple[str, str, str]:
    if not SLUG.fullmatch(source) or not VERSION.fullmatch(version) or not DIGEST.fullmatch(digest):
        raise ValueError("Invalid origin: public source slug, bounded version and sha256 digest required")
    return source, version, digest

def validate_id(value: str) -> None:
    if not isinstance(value, str) or not NODE_ID.fullmatch(value):
        raise ValueError("Malformed node ID")

def _private_path(path: Path) -> None:
    if path.suffix not in {".db", ".sqlite", ".sqlite3"}:
        raise ValueError("Expected a SQLite database path")
    for part in [path, *path.parents]:
        if part.is_symlink():
            raise ValueError("Symlinked database path forbidden")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if os.name == "posix":
        path.parent.chmod(0o700)
    if path.exists() and not path.is_file():
        raise ValueError("Not a regular database file")
    if path.exists() and os.name == "posix" and (path.stat().st_mode & 0o077):
        raise ValueError("Existing database accessible by other users")

class LocalRegistry:
    def __init__(self, filename: str | Path):
        self.filename = Path(filename).expanduser().absolute()
        _private_path(self.filename)
        self.db = sqlite3.connect(self.filename, timeout=5, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=5000")
        # Each physical computer owns its own SQLite file; never use WAL on NFS/SMB.
        self.db.execute("PRAGMA journal_mode=WAL")
        if os.name == "posix":
            self.filename.chmod(0o600)
        self.db.executescript(SCHEMA)
        found = self.db.execute("SELECT value FROM registry_meta WHERE key='schema_version'").fetchone()
        if found is None:
            self.db.execute("INSERT INTO registry_meta(key,value) VALUES('schema_version','1')")
        elif found[0] != "1":
            raise ValueError("Unsupported SQLite schema; migration required")

    def __enter__(self) -> "LocalRegistry":
        return self

    def __exit__(self, *_: object) -> None:
        self.db.close()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        else:
            self.db.execute("COMMIT")

    def _event(self, node_id: str, kind: str, detail: dict) -> None:
        self.db.execute(
            "INSERT INTO event_log(node_id,kind,detail_json,created_utc) VALUES(?,?,?,?)",
            (node_id, kind, json.dumps(detail, sort_keys=True), utc_now()),
        )

    def enroll(self, kind: str, *, operator_id: str | None = None,
               computer_id: str | None = None, source: str | None = None,
               version: str | None = None, digest: str | None = None) -> str:
        if kind not in KINDS:
            raise ValueError("Unsupported node kind")
        manifest = None
        if kind == "agent":
            if not all((operator_id, computer_id, source, version, digest)):
                raise ValueError("Agent needs existing operator/computer and origin")
            manifest = origin(source, version, digest)
        elif any(x is not None for x in (operator_id, computer_id, source, version, digest)):
            raise ValueError("Only agents can bind operator/computer/origin")
        node_id = f"{kind}_{uuid.uuid4().hex}"
        with self.transaction():
            if kind == "agent":
                for target, expected in ((operator_id, "human"), (computer_id, "computer")):
                    validate_id(target)
                    record = self.db.execute("SELECT kind FROM nodes WHERE id=?", (target,)).fetchone()
                    if record is None or record["kind"] != expected:
                        raise ValueError("Unenrolled operator or computer")
            self.db.execute("""INSERT INTO nodes
                (id,kind,operator_id,computer_id,origin_source,origin_version,origin_digest,created_utc)
                VALUES(?,?,?,?,?,?,?,?)""",
                (node_id, kind, operator_id, computer_id,
                 manifest[0] if manifest else None, manifest[1] if manifest else None,
                 manifest[2] if manifest else None, utc_now()))
            if manifest:
                self.db.execute("""INSERT INTO agent_versions
                    (agent_id,source,version,digest,recorded_utc,reason) VALUES(?,?,?,?,?,?)""",
                    (node_id, *manifest, utc_now(), "enrollment"))
            self._event(node_id, "enrolled", {"kind": kind})
        return node_id

    def capabilities(self, node_id: str, skill_ids: list[str], *, known: set[str]) -> dict:
        validate_id(node_id)
        if len(skill_ids) > 500 or any(not isinstance(x, str) or x not in known for x in skill_ids):
            raise ValueError("Unrecognized capability")
        ids = sorted(set(skill_ids))
        with self.transaction():
            if not self.db.execute("SELECT 1 FROM nodes WHERE id=?", (node_id,)).fetchone():
                raise ValueError("Unknown node")
            previous = {r[0] for r in self.db.execute(
                "SELECT skill_id FROM node_skills WHERE node_id=?", (node_id,))}
            if previous != set(ids):
                self.db.execute("DELETE FROM node_skills WHERE node_id=?", (node_id,))
                self.db.executemany(
                    "INSERT INTO node_skills(node_id,skill_id,evidence_state) VALUES(?,?,?)",
                    [(node_id, name, "self-declared") for name in ids])
                self.db.execute("UPDATE nodes SET review_state='pending' WHERE id=?", (node_id,))
                self.db.execute("""UPDATE grant_proposals SET state='invalidated'
                    WHERE node_id=? AND state='pending'""", (node_id,))
                self._event(node_id, "skills_changed", {"count": len(ids)})
        return {"node_id": node_id, "capabilities_recorded": len(ids),
                "review_state": "pending", "effective_privileges": 0}

    def upgrade(self, agent_id: str, *, source: str, version: str, digest: str) -> dict:
        validate_id(agent_id)
        manifest = origin(source, version, digest)
        with self.transaction():
            old = self.db.execute("SELECT * FROM nodes WHERE id=? AND kind='agent'", (agent_id,)).fetchone()
            if old is None:
                raise ValueError("Unknown agent")
            changed = (old["origin_source"],old["origin_version"],old["origin_digest"]) != manifest
            if changed:
                self.db.execute("""UPDATE nodes SET origin_source=?, origin_version=?, origin_digest=?,
                    origin_assurance='unverified',review_state='pending' WHERE id=?""",
                    (*manifest, agent_id))
                self.db.execute("DELETE FROM node_skills WHERE node_id=?", (agent_id,))
                self.db.execute("""UPDATE grant_proposals SET state='invalidated'
                    WHERE node_id=? AND state='pending'""", (agent_id,))
                self.db.execute("""INSERT INTO agent_versions(agent_id,source,version,digest,recorded_utc,reason)
                    VALUES(?,?,?,?,?,?)""", (agent_id, *manifest, utc_now(), "version_change"))
                self._event(agent_id, "agent_origin_changed", {"reassessment_required": True})
        return {"node_id": agent_id, "origin_changed": changed,
                "reassessment_required": changed, "effective_privileges": 0,
                "authorization": "deny-until-trusted-review"}

    def propose(self, node_id: str, skill_id: str, action: str, *, known: set[str]) -> str:
        validate_id(node_id)
        if skill_id not in known or action not in {"skill.execute","pr.propose","pr.review","pr.merge"}:
            raise ValueError("Unsupported skill/action")
        token = f"proposal_{uuid.uuid4().hex}"
        with self.transaction():
            if not self.db.execute("SELECT 1 FROM nodes WHERE id=?", (node_id,)).fetchone():
                raise ValueError("Unknown node")
            self.db.execute("INSERT INTO grant_proposals VALUES(?,?,?,?,?,?)",
                            (token,node_id,skill_id,action,"pending",utc_now()))
            self._event(node_id, "proposed", {"skill_id":skill_id,"action":action})
        return token

    def summary(self) -> dict:
        counts = {kind:self.db.execute("SELECT COUNT(*) FROM nodes WHERE kind=?",(kind,)).fetchone()[0]
                  for kind in sorted(KINDS)}
        outstanding = self.db.execute(
            "SELECT COUNT(*) FROM grant_proposals WHERE state='pending'").fetchone()[0]
        return {"schema_version":1,"private_local_only":True,"nodes_by_kind":counts,
                "outstanding_proposals":outstanding,"effective_repository_grants":0}

    @staticmethod
    def authorize(*_: object, **__: object) -> bool:
        # Only authenticated GitHub permissions and trusted review can permit PR actions.
        return False
