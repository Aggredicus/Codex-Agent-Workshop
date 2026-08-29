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


def test_substrings_do_not_activate_unrelated_specialists():
    team = load_team(ROOT / "teams" / "permaculture-works" / "team.toml")

    leads = build_plan(
        team,
        "Find 20 qualified leads in West Michigan for permaculture design services, draft outreach, and build a follow-up plan.",
        mode="multi",
    )
    lead_workers = {assignment.role for assignment in leads.waves[1]}
    assert "lead-development" in lead_workers
    assert "planting-designer" not in lead_workers  # 'guild' must not match 'qualified'
    assert "ecological-designer" not in lead_workers

    campaign = build_plan(
        team,
        "Create an SEO content campaign to generate qualified permaculture design leads from Grand Rapids.",
        mode="multi",
    )
    campaign_workers = {assignment.role for assignment in campaign.waves[1]}
    assert "marketing-content" in campaign_workers
    assert "automation-engineer" not in campaign_workers  # 'api' must not match 'campaign'


def test_reviewer_coverage_can_follow_selected_specialist():
    team = load_team(ROOT / "teams" / "permaculture-works" / "team.toml")
    plan = build_plan(
        team,
        "Design swales and berms for an eroding sloped property with drainage and pond opportunities.",
        mode="multi",
    )
    work_roles = {assignment.role for assignment in plan.waves[1]}
    review_roles = {assignment.role for assignment in plan.waves[2]}
    assert "water-earthworks" in work_roles
    assert "science-reviewer" in review_roles
    assert "design-quality-reviewer" in review_roles
