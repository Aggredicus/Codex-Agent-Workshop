# Codex Agent Workshop — Agent Map

Start here. This file is a map, not the full manual.

## Read order

1. `README.md` — product and quick start.
2. `WORKFLOW.md` — task lifecycle, evidence, and approval boundaries.
3. `SPEC.md` — architecture and invariants when changing the workshop itself.
4. `teams/<team>/team.toml` — the active organization and role definitions.
5. `.agents/skills/<skill>/SKILL.md` — procedures selected by the task/role.

Use `docs/` only when the current task needs deeper context.

## Source of truth

```text
tracked objective / human instruction   task intent
teams/*/team.toml                        organization + routing policy
.agents/skills/*/SKILL.md                reusable procedures
WORKFLOW.md                              lifecycle / consequence policy
SPEC.md                                  architecture
Git / PR / CI                            implementation + review evidence
memory/                                  reviewed reusable lessons
```

Do not invent a second project-state database or treat generated output as more authoritative than these sources.

## Before meaningful work

```bash
caw validate
caw plan --team <team> --goal "<objective>"
```

Use `caw prompt` when a pasteable harness instruction is useful.

## Work contract

Agent-executable work should make these explicit enough to proceed safely:

```text
objective
inputs
outputs
evidence / acceptance criteria
stop conditions
non-goals
risk / human-gated consequence
```

If details are missing, make the safest useful progress that does not depend on guessing, then surface the missing decision.

## Context efficiency

- Use the minimum sufficient roles.
- Load only the role's relevant context paths plus task inputs.
- Prefer compact handoffs over replaying full conversations.
- Parallelize only independent work.
- Do not invoke an expensive/deep role merely because it exists.
- Escalate model/context budget when evidence shows the task needs it.

## Execution modes

- `single`: one model executes roles sequentially.
- `multi`: independent roles may be delegated to native subagents.
- `symphony`: tracker/task lifecycle is the outer loop; CAW is the inner team compiler.
- `auto`: let the available harness choose while preserving the same role plan.

The semantic result should not depend on native subagents being available.

## Approval boundary

Agents can prepare high-consequence work. They must stop before unapproved live effects such as payments, binding contracts, legal/tax filings, credential/access changes, sensitive customer disclosure, destructive actions, or other explicitly gated consequences.

## Evidence-triggered learning

Do not create an improvement issue just because a Skill or role ran.

Use `docs/SELF_IMPROVEMENT.md` and `.agents/skills/improve-workshop/SKILL.md` when repeated corrections, reviewer findings, measurable cost regressions, tool failures, routing errors, or customer feedback show a reusable improvement opportunity.

## Verification

When changing this repository itself:

```bash
caw validate
pytest -q
```

Keep changes reviewable. Do not merge consequential policy/runtime changes without the required human decision.
