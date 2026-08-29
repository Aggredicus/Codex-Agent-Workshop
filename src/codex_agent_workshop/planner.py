from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import re

from .config import Role, Team

TOKEN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
STOPWORDS = {"and", "the", "for", "with", "from", "into", "prepare", "client", "work", "business", "task", "review", "create", "make"}
MIN_WORKER_SCORE = 3


@dataclass(frozen=True)
class Assignment:
    role: str
    title: str
    phase: str
    reason: str
    mission: str
    challenge: tuple[str, ...]
    skills: tuple[str, ...]
    context: tuple[str, ...]
    model_class: str
    context_budget_tokens: int
    handoff_budget_tokens: int
    risk_ceiling: str
    outputs: tuple[str, ...]


@dataclass(frozen=True)
class WorkPlan:
    team: str
    team_name: str
    goal: str
    mode: str
    max_parallel: int
    waves: tuple[tuple[Assignment, ...], ...]
    final_integrator: str
    handoff_contract: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["waves"] = [[asdict(item) for item in wave] for wave in self.waves]
        return data


def _plural_forms(token: str) -> set[str]:
    forms = {token}
    if len(token) <= 2:
        return forms
    if token.endswith("y") and not token.endswith(("ay", "ey", "iy", "oy", "uy")):
        forms.add(token[:-1] + "ies")
    elif token.endswith(("s", "x", "z", "ch", "sh")):
        forms.add(token + "es")
    else:
        forms.add(token + "s")
    return forms


def _keyword_matches(keyword: str, goal_tokens: tuple[str, ...]) -> bool:
    keyword_tokens = tuple(TOKEN.findall(keyword.lower()))
    if not keyword_tokens:
        return False
    width = len(keyword_tokens)
    if width > len(goal_tokens):
        return False
    for start in range(len(goal_tokens) - width + 1):
        window = goal_tokens[start:start + width]
        if all(actual in _plural_forms(expected) for actual, expected in zip(window, keyword_tokens)):
            return True
    return False


def _score(role: Role, goal: str) -> tuple[int, list[str]]:
    goal_tokens = tuple(TOKEN.findall(goal.lower()))
    tokens = {token for token in goal_tokens if token not in STOPWORDS}
    score = 0
    reasons: list[str] = []
    for keyword in role.keywords:
        if _keyword_matches(keyword, goal_tokens):
            keyword_width = len(TOKEN.findall(keyword.lower()))
            score += 4 if keyword_width > 1 else 3
            reasons.append(f"matched {keyword!r}")
    searchable_tokens = set(TOKEN.findall(f"{role.title} {role.mission}".lower()))
    overlap = sorted(token for token in tokens if token in searchable_tokens)
    if overlap:
        score += min(len(overlap), 4)
        reasons.append("mission overlap: " + ", ".join(overlap[:4]))
    return score, reasons


def _assignment(role: Role, reason: str) -> Assignment:
    return Assignment(
        role=role.id,
        title=role.title,
        phase=role.phase,
        reason=reason,
        mission=role.mission,
        challenge=role.challenge,
        skills=role.skills,
        context=role.context,
        model_class=role.model_class,
        context_budget_tokens=role.context_budget_tokens,
        handoff_budget_tokens=role.handoff_budget_tokens,
        risk_ceiling=role.risk_ceiling,
        outputs=role.outputs,
    )


def build_plan(team: Team, goal: str, *, mode: str = "auto") -> WorkPlan:
    if not goal.strip():
        raise ValueError("goal must not be empty")
    if mode == "auto":
        mode = team.default_mode
    if mode not in {"auto", "single", "multi", "symphony"}:
        raise ValueError(f"unsupported execution mode {mode!r}")

    scored = {role.id: _score(role, goal) for role in team.roles}

    planners = [
        role for role in team.roles
        if role.phase == "plan" and (role.always or scored[role.id][0] > 0)
    ]
    if not planners:
        planners = [next(role for role in team.roles if role.phase == "plan")]

    worker_candidates = [
        (scored[role.id][0], role, scored[role.id][1])
        for role in team.roles if role.phase == "work"
    ]
    worker_candidates.sort(key=lambda row: (-row[0], row[1].id))
    selected_workers = [row for row in worker_candidates if row[0] >= MIN_WORKER_SCORE][:team.max_specialists]
    if not selected_workers:
        selected_workers = worker_candidates[:min(2, team.max_specialists)]
    selected_worker_ids = {role.id for _, role, _ in selected_workers}

    reviewers = [
        role for role in team.roles
        if role.phase == "review"
        and (
            role.always
            or scored[role.id][0] >= MIN_WORKER_SCORE
            or role.id == team.default_reviewer
            or bool(selected_worker_ids.intersection(role.review_for))
        )
    ]
    unique_reviewers: list[Role] = []
    seen_review: set[str] = set()
    for role in reviewers:
        if role.id not in seen_review:
            seen_review.add(role.id)
            unique_reviewers.append(role)

    plan_wave = tuple(
        _assignment(role, "planning role selected by team policy" if role.always else "planning role matched the objective")
        for role in planners
    )
    work_wave = tuple(
        _assignment(role, "; ".join(reasons) if reasons else "fallback specialist")
        for _, role, reasons in selected_workers
    )
    review_wave = tuple(
        _assignment(
            role,
            "default independent reviewer"
            if role.id == team.default_reviewer
            else (
                "review policy covers selected role(s): "
                + ", ".join(sorted(selected_worker_ids.intersection(role.review_for)))
                if selected_worker_ids.intersection(role.review_for)
                else "; ".join(scored[role.id][1]) or "review policy"
            ),
        )
        for role in unique_reviewers
    )
    integrator = team.by_id[team.final_integrator]
    integration_wave = (
        _assignment(integrator, "integrate specialist handoffs, reviewer findings, and unresolved dissent"),
    )

    return WorkPlan(
        team=team.id,
        team_name=team.name,
        goal=goal.strip(),
        mode=mode,
        max_parallel=1 if mode == "single" else team.max_parallel,
        waves=(plan_wave, work_wave, review_wave, integration_wave),
        final_integrator=team.final_integrator,
        handoff_contract=(
            "summary",
            "claims_and_decisions",
            "evidence_or_source_paths",
            "assumptions",
            "risks_and_limitations",
            "open_questions",
            "recommended_next_action",
            "human_decision_needed",
        ),
    )


def render_plan(plan: WorkPlan) -> str:
    lines = [
        f"Team: {plan.team_name} ({plan.team})",
        f"Mode: {plan.mode}",
        f"Goal: {plan.goal}",
        "",
    ]
    for index, wave in enumerate(plan.waves, start=1):
        lines.append(f"Wave {index}:")
        for item in wave:
            skills = ", ".join(item.skills) or "none"
            context = ", ".join(item.context) or "task inputs only"
            lines.append(f"  - {item.role} [{item.model_class}, risk<={item.risk_ceiling}] — {item.reason}")
            lines.append(f"    skills: {skills}")
            lines.append(f"    context: {context}")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_prompt(plan: WorkPlan) -> str:
    strategy = {
        "single": "Execute each assignment sequentially in a single model. Explicitly announce the active role and preserve disagreements.",
        "multi": "Delegate independent assignments within each wave to separate subagents when the harness supports it; otherwise fall back to the single-agent strategy.",
        "symphony": "Treat the tracker task as the outer lifecycle. Execute this internal role plan in the isolated task workspace and return a review-ready handoff.",
        "auto": "Use the strongest available execution strategy while preserving the same role plan and approval boundaries.",
    }[plan.mode]
    return (
        "You are the coordinator for a Codex Agent Workshop run.\n\n"
        "Read AGENTS.md and WORKFLOW.md before acting.\n\n"
        f"Execution strategy: {strategy}\n\n"
        "Rules:\n"
        "- Use only the minimum selected roles; do not add departments without a concrete need.\n"
        "- Load only each role's listed context plus task-specific inputs.\n"
        "- Roles in the same work wave may run in parallel only when independent.\n"
        "- Require a compact handoff from each role; do not forward full hidden reasoning or full transcripts.\n"
        "- Reviewers must challenge claims against evidence and role-specific failure modes.\n"
        "- Stop before any human-gated live consequence in WORKFLOW.md.\n"
        "- Finish with one integrated handoff stating outputs, evidence, risks, and the exact human decision needed.\n\n"
        "Compiled work plan:\n"
        + json.dumps(plan.to_dict(), indent=2, ensure_ascii=False)
    )
