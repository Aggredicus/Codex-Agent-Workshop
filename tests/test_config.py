from pathlib import Path

from codex_agent_workshop.config import discover_teams, load_team, validate_team


ROOT = Path(__file__).resolve().parents[1]


def test_discover_example_teams():
    teams = discover_teams(ROOT)
    assert {"solo-llc", "permaculture-works"}.issubset(teams)


def test_solo_team_validates():
    team = load_team(ROOT / "teams" / "solo-llc" / "team.toml")
    assert validate_team(team) is None
    assert team.final_integrator == "chief-of-staff"
    assert team.default_reviewer == "quality-reviewer"


def test_permaculture_team_has_unique_valid_roles():
    team = load_team(ROOT / "teams" / "permaculture-works" / "team.toml")
    assert validate_team(team) is None
    ids = [role.id for role in team.roles]
    assert len(ids) == len(set(ids))
    assert "ecological-designer" in ids
    assert "science-reviewer" in ids
