"""Local-only, fail-closed SQLite registry regression tests."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codex_agent_workshop.local_registry import LocalRegistry

D1 = "sha256:" + "a" * 64
D2 = "sha256:" + "b" * 64
KNOWN = {"python", "agent-orchestration", "secrets-management"}

def test_three_node_kinds_have_opaque_ids(tmp_path):
    with LocalRegistry(tmp_path / "private" / "nodes.sqlite3") as r:
        human = r.enroll("human")
        computer = r.enroll("computer")
        agent = r.enroll("agent", operator_id=human, computer_id=computer,
                         source="codex", version="1.0", digest=D1)
        assert len({human, computer, agent}) == 3
        assert human.startswith("human_") and computer.startswith("computer_")
        assert agent.startswith("agent_")
        assert r.summary()["nodes_by_kind"] == {"agent":1,"computer":1,"human":1}
        assert not r.authorize(agent, "pr.merge")

def test_agent_upgrade_requires_reassessment(tmp_path):
    with LocalRegistry(tmp_path / "private" / "nodes.sqlite3") as r:
        human = r.enroll("human")
        computer = r.enroll("computer")
        agent = r.enroll("agent",operator_id=human,computer_id=computer,
                         source="codex",version="1",digest=D1)
        r.capabilities(agent, ["python"], known=KNOWN)
        r.propose(agent, "python", "skill.execute", known=KNOWN)
        assert r.upgrade(agent, source="codex",version="1",digest=D1)["origin_changed"] is False
        assert r.db.execute("SELECT COUNT(*) FROM node_skills").fetchone()[0] == 1
        changed = r.upgrade(agent,source="codex",version="2",digest=D2)
        assert changed["origin_changed"] is True
        assert changed["effective_privileges"] == 0
        assert r.db.execute("SELECT COUNT(*) FROM node_skills").fetchone()[0] == 0
        assert r.db.execute("SELECT COUNT(*) FROM agent_versions").fetchone()[0] == 2
        assert r.summary()["outstanding_proposals"] == 0
        assert not r.authorize(agent, "pr.merge")

def test_identity_and_skills_fail_closed(tmp_path):
    with LocalRegistry(tmp_path / "private" / "nodes.sqlite3") as r:
        pc = r.enroll("computer")
        with pytest.raises(ValueError):
            r.enroll("agent",operator_id=pc,computer_id=pc,
                     source="codex",version="1",digest=D1)
        human = r.enroll("human")
        with pytest.raises(ValueError):
            r.capabilities(human,["person@example.com"],known=KNOWN)
        assert r.db.execute("SELECT COUNT(*) FROM node_skills").fetchone()[0] == 0
        with pytest.raises(ValueError):
            r.propose(human,"python","policy.vote",known=KNOWN)
        r.capabilities(human,["python","python"],known=KNOWN)
        assert r.db.execute("SELECT COUNT(*) FROM node_skills").fetchone()[0] == 1
        r.propose(human,"python","pr.merge",known=KNOWN)
        assert r.summary()["effective_repository_grants"] == 0
        r.capabilities(human,["agent-orchestration"],known=KNOWN)
        assert r.summary()["outstanding_proposals"] == 0

def test_local_db_survives_restart(tmp_path):
    path = tmp_path / "private" / "nodes.sqlite3"
    with LocalRegistry(path) as r:
        r.enroll("computer")
    with LocalRegistry(path) as r:
        assert r.summary()["nodes_by_kind"]["computer"] == 1
        assert r.db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert r.db.execute("PRAGMA journal_mode").fetchone()[0] == "wal"

def test_refuses_symlinks_and_untrusted_existing_file(tmp_path):
    path = tmp_path / "private" / "original.sqlite3"
    with LocalRegistry(path):
        pass
    symlink = tmp_path / "private" / "link.sqlite3"
    symlink.symlink_to(path)
    with pytest.raises(ValueError):
        LocalRegistry(symlink)
