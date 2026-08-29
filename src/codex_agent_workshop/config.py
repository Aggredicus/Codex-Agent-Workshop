from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import tomllib

VALID_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_PHASES = {"plan", "work", "review"}
VALID_MODEL_CLASSES = {"fast", "balanced", "deep"}
VALID_RISK = {"low", "medium", "high"}


@dataclass(frozen=True)
class Role:
    id: str
    title: str
    phase: str
    mission: str
    challenge: tuple[str, ...]
    keywords: tuple[str, ...]
    skills: tuple[str, ...]
    context: tuple[str, ...]
    model_class: str
    context_budget_tokens: int
    handoff_budget_tokens: int
    risk_ceiling: str
    outputs: tuple[str, ...]
    review_for: tuple[str, ...] = ()
    always: bool = False


@dataclass(frozen=True)
class Team:
    id: str
    name: str
    description: str
    default_mode: str
    max_parallel: int
    max_specialists: int
    final_integrator: str
    default_reviewer: str
    roles: tuple[Role, ...]

    @property
    def by_id(self) -> dict[str, Role]:
        return {role.id: role for role in self.roles}


def _as_tuple(value: object, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be an array of strings")
    return tuple(value)


def load_team(path: Path) -> Team:
    with path.open("rb") as handle:
        raw = tomllib.load(handle)

    meta = raw.get("team")
    if not isinstance(meta, dict):
        raise ValueError(f"{path}: missing [team] table")

    roles_raw = raw.get("roles")
    if not isinstance(roles_raw, list) or not roles_raw:
        raise ValueError(f"{path}: at least one [[roles]] entry is required")

    roles: list[Role] = []
    for item in roles_raw:
        if not isinstance(item, dict):
            raise ValueError(f"{path}: role entries must be tables")
        role = Role(
            id=str(item.get("id", "")),
            title=str(item.get("title", "")),
            phase=str(item.get("phase", "")),
            mission=str(item.get("mission", "")),
            challenge=_as_tuple(item.get("challenge"), "challenge"),
            keywords=_as_tuple(item.get("keywords"), "keywords"),
            skills=_as_tuple(item.get("skills"), "skills"),
            context=_as_tuple(item.get("context"), "context"),
            model_class=str(item.get("model_class", "balanced")),
            context_budget_tokens=int(item.get("context_budget_tokens", 12000)),
            handoff_budget_tokens=int(item.get("handoff_budget_tokens", 1800)),
            risk_ceiling=str(item.get("risk_ceiling", "medium")),
            outputs=_as_tuple(item.get("outputs"), "outputs"),
            review_for=_as_tuple(item.get("review_for"), "review_for"),
            always=bool(item.get("always", False)),
        )
        roles.append(role)

    team = Team(
        id=str(meta.get("id", "")),
        name=str(meta.get("name", "")),
        description=str(meta.get("description", "")),
        default_mode=str(meta.get("default_mode", "auto")),
        max_parallel=int(meta.get("max_parallel", 4)),
        max_specialists=int(meta.get("max_specialists", 4)),
        final_integrator=str(meta.get("final_integrator", "")),
        default_reviewer=str(meta.get("default_reviewer", "")),
        roles=tuple(roles),
    )
    validate_team(team, source=str(path))
    return team


def validate_team(team: Team, *, source: str = "<team>") -> None:
    problems: list[str] = []
    if not VALID_ID.fullmatch(team.id):
        problems.append(f"invalid team id {team.id!r}")
    if not team.name:
        problems.append("team name is required")
    if team.default_mode not in {"auto", "single", "multi", "symphony"}:
        problems.append(f"invalid default_mode {team.default_mode!r}")
    if team.max_parallel < 1:
        problems.append("max_parallel must be >= 1")
    if team.max_specialists < 1:
        problems.append("max_specialists must be >= 1")

    seen: set[str] = set()
    for role in team.roles:
        if not VALID_ID.fullmatch(role.id):
            problems.append(f"invalid role id {role.id!r}")
        if role.id in seen:
            problems.append(f"duplicate role id {role.id!r}")
        seen.add(role.id)
        if not role.title or not role.mission:
            problems.append(f"role {role.id!r} requires title and mission")
        if role.phase not in VALID_PHASES:
            problems.append(f"role {role.id!r} has invalid phase {role.phase!r}")
        if role.model_class not in VALID_MODEL_CLASSES:
            problems.append(f"role {role.id!r} has invalid model_class {role.model_class!r}")
        if role.risk_ceiling not in VALID_RISK:
            problems.append(f"role {role.id!r} has invalid risk_ceiling {role.risk_ceiling!r}")
        if role.context_budget_tokens < 1000:
            problems.append(f"role {role.id!r} context budget is unrealistically small")
        if role.handoff_budget_tokens < 200:
            problems.append(f"role {role.id!r} handoff budget is unrealistically small")

    for role in team.roles:
        if role.review_for and role.phase != "review":
            problems.append(f"role {role.id!r} may use review_for only with phase='review'")
        unknown = sorted(set(role.review_for) - seen)
        if unknown:
            problems.append(f"role {role.id!r} review_for references unknown roles: {', '.join(unknown)}")

    if team.final_integrator not in seen:
        problems.append("final_integrator must name an existing role")
    if team.default_reviewer not in seen:
        problems.append("default_reviewer must name an existing role")
    elif team.by_id[team.default_reviewer].phase != "review":
        problems.append("default_reviewer must use phase='review'")
    if not any(role.phase == "plan" for role in team.roles):
        problems.append("at least one planning role is required")
    if not any(role.phase == "work" for role in team.roles):
        problems.append("at least one work role is required")
    if not any(role.phase == "review" for role in team.roles):
        problems.append("at least one review role is required")

    if problems:
        raise ValueError(f"{source}: " + "; ".join(problems))


def discover_teams(root: Path) -> dict[str, Path]:
    teams_dir = root / "teams"
    if not teams_dir.exists():
        return {}
    return {path.parent.name: path for path in sorted(teams_dir.glob("*/team.toml"))}


def resolve_team(root: Path, slug: str) -> Team:
    path = root / "teams" / slug / "team.toml"
    if not path.exists():
        choices = ", ".join(discover_teams(root)) or "<none>"
        raise ValueError(f"unknown team {slug!r}; available: {choices}")
    return load_team(path)
