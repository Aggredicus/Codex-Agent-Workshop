"""CAW owns the canonical contract and public skill inventory, not a local runtime."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "caw-law-work-packet.v1.json"
EXAMPLE = ROOT / "contracts" / "fixtures" / "caw-law-work-packet.example.json"

def test_canonical_contract_is_versioned_and_never_claims_authority():
    cfg = json.loads(CONTRACT.read_text("utf-8"))
    assert cfg["schema_version"] == 1
    assert cfg["contract_id"] == "caw.law.work-packet"
    assert cfg["contract_status"] == "proposal"
    assert cfg["security"]["self_grant_forbidden"] is True
    assert cfg["security"]["untrusted_packet"] is True
    required = set(cfg["required"])
    assert required <= set(cfg["fields"])
    assert {"task_id","required_skills","allowed_paths","forbidden_paths",
            "requested_agent","governance","stop_conditions"} <= required
    assert cfg["fields"]["governance"]["fields"]["approval_state"]["enum"] == [
        "proposal", "needs-human-review"
    ]

def test_public_sample_follows_contract_field_names():
    cfg = json.loads(CONTRACT.read_text("utf-8"))
    packet = json.loads(EXAMPLE.read_text("utf-8"))
    assert set(cfg["required"]) <= set(packet)
    assert set(packet) <= set(cfg["fields"])
    assert packet["governance"]["approval_state"] == "proposal"
    assert packet["requested_agent"]["origin_digest"].startswith("sha256:")
    assert len(packet["requested_agent"]["origin_digest"]) == 71
    allowed = {x["id"] for x in json.loads(
        (ROOT / "skill-inventory" / "taxonomy.json").read_text("utf-8")
    )["categories"]}
    assert set(packet["required_skills"]) <= allowed
    assert not any("@" in json.dumps(packet) for _ in [0])

def test_skill_inventory_generator_is_current_and_privacy_scoped():
    command = [sys.executable,str(ROOT / "scripts" / "build_skill_inventory.py"),"--check"]
    result = subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=30)
    assert result.returncode == 0,result.stdout+result.stderr
    data = json.loads((ROOT / "skill-inventory" / "inventory.json").read_text("utf-8"))
    assert data["subject"] == "repository-artifacts-only"
    assert data["no_person_or_agent_competence_claims"] is True
    assert all("node_id" not in row for row in data["capabilities"])

def test_private_runtime_not_duplicated_in_caw():
    assert not (ROOT / "src" / "codex_agent_workshop" / "local_registry.py").exists()
    assert not (ROOT / "scripts" / "node_registry.py").exists()
