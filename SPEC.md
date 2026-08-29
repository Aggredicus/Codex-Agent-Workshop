# Codex Agent Workshop Specification

Status: MVP v0.1

Purpose: Define a small, harness-neutral system for expressing agent organizations and compiling real objectives into efficient, reviewable execution plans.

## 1. Problem

Agent harnesses increasingly support tools, Skills, subagents, worktrees, and durable orchestration. What remains organization-specific is:

- which professional roles exist,
- when each role should be used,
- what context each role needs,
- which procedures/Skills it follows,
- what it must challenge,
- how much context/compute it should consume,
- how roles exchange evidence,
- which consequences require a human,
- how the organization learns from outcomes.

CAW stores that layer in the repository.

## 2. Goals

1. Let a user create an arbitrary agent team without writing an orchestration framework.
2. Compile a natural-language objective into the minimum sufficient role set.
3. Keep role context small and explicit.
4. Express the same plan for single-agent and multi-agent harnesses.
5. Fit naturally inside Symphony's tracker/workspace model.
6. Preserve independent review and real-world approval boundaries.
7. Improve from evidence without uncontrolled self-modification.
8. Be useful for knowledge/business work, not only software implementation.

## 3. Sources of truth

| Concern | Authority |
|---|---|
| task objective / status | configured tracker or direct human instruction |
| organization / routing | `teams/*/team.toml` |
| procedures | `.agents/skills/*/SKILL.md` |
| lifecycle / approvals | `WORKFLOW.md` |
| architecture | `SPEC.md` |
| implementation | Git source |
| verification | tests / CI / eval evidence |
| durable lessons | reviewed `memory/` entries |

Generated plans and prompts are projections, not authority.

## 4. Team definition

A team is a TOML document with one `[team]` table and one or more `[[roles]]` tables.

### Team fields

```text
id
name
description
default_mode
max_parallel
max_specialists
final_integrator
default_reviewer
```

### Role fields

```text
id
title
phase                 plan | work | review
mission
challenge[]
keywords[]
skills[]
context[]
model_class            fast | balanced | deep
context_budget_tokens
handoff_budget_tokens
risk_ceiling           low | medium | high
outputs[]
always                  optional boolean
```

Role descriptions encode a professional mandate and productive bias. They are not character biographies.

## 5. Deterministic task compiler

Input:

```text
team + objective + execution mode
```

Output:

```text
planning wave
work wave
review wave
integration wave
```

### Selection v0.1

- planning roles marked `always=true` are included;
- work roles are ranked by explicit keyword and mission/title overlap;
- only positive-matching work roles are selected, capped by `max_specialists`;
- when no specialist matches, use a small fallback subset rather than failing silently;
- review roles marked `always=true`, matching the objective, or equal to the default reviewer are included;
- `final_integrator` closes the plan.

The ranking is deliberately deterministic and inspectable. A semantic/model router may be added later only with evaluations proving it improves selection enough to justify its cost and nondeterminism.

## 6. Work waves

Roles in a wave are candidates for parallel execution. A harness must still check runtime dependencies.

```text
plan -> work -> review -> integration
```

The MVP does not encode arbitrary DAG edges because most team coordination can begin with this shape. Add explicit dependencies only when real workflows prove the four-wave model inadequate.

## 7. Context policy

A role's `context` list is a progressive-disclosure hint, not an instruction to concatenate every matching file into the prompt.

A harness should:

1. inspect the role's context paths;
2. retrieve only the files/sections needed for the objective;
3. stay near `context_budget_tokens` where practical;
4. summarize large evidence into citations/paths;
5. pass compact handoffs between roles.

Task-specific user attachments and connected-system data may supplement repository context.

## 8. Handoff contract

Each assignment returns a compact packet containing:

```text
summary
claims_and_decisions
evidence_or_source_paths
assumptions
risks_and_limitations
open_questions
recommended_next_action
human_decision_needed
```

A harness should not ask roles to reveal hidden chain-of-thought. Exchange conclusions and evidence.

## 9. Model routing

The workshop stores abstract model classes, not names:

```text
fast      narrow, cheap, high-volume work
balanced  general professional work
deep      difficult synthesis / adversarial review / architecture
```

A harness adapter maps these classes to the current model inventory.

Escalation is justified by task difficulty or review evidence. Expensive models should not receive routine work by default.

## 10. Execution modes

### single

One model executes assignments sequentially. `max_parallel=1`.

### multi

A capable harness may run independent assignments in the same wave concurrently.

### symphony

The tracker issue is the outer work unit. Symphony handles eligibility, workspace isolation, retries, and worker lifetime; CAW compiles the team inside the task workspace.

### auto

The available harness chooses the strongest supported mode without changing the semantic role plan.

## 11. Codex App Server boundary

A future programmatic adapter may use Codex App Server to:

- create/resume threads,
- start turns,
- stream tool/item events,
- route approvals,
- record token/latency telemetry,
- bound concurrent role work.

The adapter must not duplicate organization policy already held in Team TOML and `WORKFLOW.md`.

## 12. Consequence policy

The system distinguishes **doing cognitive/preparatory work** from **activating external consequences**.

Business roles may research, draft, analyze, calculate, prepare proposals, prepare client deliverables, organize project work, prepare marketing content, prepare bookkeeping classifications, and prepare operational plans.

Live consequential actions remain policy-gated.

## 13. Self-improvement

A run becomes an improvement proposal only when it is actionable.

Triggers include:

```text
human correction
failed acceptance criterion
repeated reviewer objection
measurable token/cost regression
unnecessary role fan-out
missing skill/tool/context
repeated manual workaround
customer-facing defect
```

Improvement proposals must state evidence, hypothesis, change, expected benefit, risk, representative evals, and rollback.

## 14. Non-goals for MVP

- No custom replacement for GitHub/Linear task state.
- No mandatory Proxmox dependency.
- No custom vector database.
- No opaque autonomous policy mutation.
- No requirement for native subagents.
- No attempt to simulate an entire corporation on every task.
- No token optimization that lowers output quality below the configured eval bar.
