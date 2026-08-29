from pathlib import Path

from codex_agent_workshop.config import load_team
from codex_agent_workshop.planner import build_plan, render_prompt


ROOT = Path(__file__).resolve().parents[1]


def ids(plan):
    return {assignment.role for wave in plan.waves for assignment in wave}


def test_permaculture_design_routes_domain_roles():
    team = load_team(ROOT / "teams" / "permaculture-works" / "team.toml")
    plan = build_plan(
        team,
        "Prepare a client permaculture site design with planting strategy, site soil and water research, and cost estimate.",
        mode="multi",
    )
    selected = ids(plan)
    assert "chief-of-staff" in selected
    assert "site-research" in selected
    assert "ecological-designer" in selected
    assert "planting-designer" in selected
    assert "estimating-proposals" in selected
    assert "science-reviewer" in selected
    assert "design-quality-reviewer" in selected

    work_wave = plan.waves[1]
    assert len(work_wave) <= team.max_specialists


def test_single_mode_serializes_parallelism_and_routes_growth():
    team = load_team(ROOT / "teams" / "solo-llc" / "team.toml")
    plan = build_plan(
        team,
        "Create a marketing campaign and sales follow-up plan for qualified leads.",
        mode="single",
    )
    selected = ids(plan)
    assert plan.max_parallel == 1
    assert "marketing" in selected
    assert "sales-growth" in selected


def test_prompt_contains_harness_and_human_gate_guidance():
    team = load_team(ROOT / "teams" / "solo-llc" / "team.toml")
    plan = build_plan(team, "Review pricing, cash flow, and overdue invoices.", mode="single")
    prompt = render_prompt(plan)
    assert "single model" in prompt.lower()
    assert "human-gated" in prompt.lower()
    assert "finance" in prompt.lower()
