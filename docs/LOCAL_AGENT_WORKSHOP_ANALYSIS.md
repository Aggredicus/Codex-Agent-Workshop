# Systematic Analysis of Local Agent Workshop

This document records the design extraction used to create Codex Agent Workshop. The goal was not to copy the older repository. It was to identify which ideas survived contact with actual use and which abstractions arrived before the runtime that needed them.

Source repository: `Aggredicus/Local-Agent-Workshop`

## 1. Instruction and arrival layer

Local Agent Workshop developed a canonical instruction spine plus harness-specific adapters. The durable lesson is excellent: a fresh agent should be able to orient from repository state rather than hidden chat history.

**Carry forward**

- repository-local instructions,
- cold-start friendliness,
- progressive disclosure,
- a short root map.

**Simplify**

- use a concise `AGENTS.md` as the primary map,
- keep detailed policy close to the subsystem it governs,
- avoid duplicating the same instruction across adapter files.

## 2. Skills

The old repository accumulated reusable Skills and later implemented deterministic discovery, validation, synchronization, and lexical selection.

**Carry forward**

- Agent Skills as reusable procedures,
- deterministic discovery before inventing a new skill,
- machine-checkable metadata,
- explicit security review for imported/untrusted procedures.

**Change**

The old global rule required a new improvement issue and durable artifact update after every skill invocation. That guaranteed an audit trail, but it also guaranteed administrative growth even when no meaningful lesson existed.

CAW uses **evidence-triggered improvement** instead:

```text
run -> cheap run record -> eval
                         |
                         +--> no material lesson: stop
                         |
                         +--> repeated/measurable lesson: improvement proposal
```

## 3. Governance and risk

The strongest old governance principle was:

> Agents may prepare sensitive work, but should stop before activating sensitive consequences without authorization.

That maps naturally to business operations and remains central to CAW.

**Carry forward**

- risk classes,
- explicit human consequence gates,
- no secret leakage,
- no self-approval for consequential actions,
- reversible preparation before live effect.

**Simplify**

Risk should choose the amount of process. Low-risk formatting should not experience the same ceremony as payments, contracts, production, or safety-critical recommendations.

## 4. Execution contract

The old Standard Execution Contract required:

```text
inputs
outputs
evidence
stop conditions
non-goals
acceptance criteria
handoff
```

This is one of the most reusable pieces of the repository and maps directly to Symphony-style issue execution.

**Carry forward nearly unchanged**, but let the tracker item remain the source of task truth.

## 5. Automation loop

The old canonical loop grew to nine named stages:

```text
cleanup
quality baseline
issue generation
grind
self-improvement
issue generation
cleanup
quality final
human decision
```

The protocol itself eventually added skip and cost-control rules, which reveals the lesson: the individual concerns were useful, but making all of them explicit ritual steps for all work was too heavy.

**CAW replacement**

Use lifecycle hooks selected by task and risk:

```text
orient -> plan -> work -> review -> integrate -> handoff
```

Then add only the needed checks:

```text
low risk:     lightweight evidence
medium risk:  reviewer + evidence
high risk:    adversarial review + explicit human consequence gate
```

## 6. Schemas and data contracts

Local Agent Workshop developed a schema registry and schemas for HyperKanban, dashboards, dependency graphs, reports, and other planned runtime records.

**Carry forward**

- schemas for interfaces that actually cross process/harness boundaries,
- deterministic validation,
- fixtures for important failure modes.

**Delay**

Do not build a large schema registry before the contracts stabilize. The MVP can use TOML configuration plus Python validation. JSON schemas can be added when an external adapter needs a stable wire format.

## 7. Runtime code

The executable Python package was much smaller than the conceptual roadmap. It primarily contained:

- CLI,
- environment doctor,
- skill discovery/selection,
- HyperKanban state helpers.

This mismatch is the clearest architectural signal from the old project:

```text
large conceptual control plane
small executable runtime
```

CAW therefore starts from executable user value: define a team, validate it, route an objective, render an execution prompt.

## 8. HyperKanban and project state

HyperKanban experimented with rich dimensions for dependency depth, workflow state, nesting, timeline, domain, agent lane, and risk.

The dimensions were useful for thinking, but a mirrored project-state system introduces synchronization and authority questions whenever GitHub Issues/PRs already hold much of the same truth.

**CAW replacement**

- tracker = planned work and status,
- Git/PR = code/artifact review boundary,
- CI/evals = evidence,
- team config = organizational routing policy.

A dashboard can later be a projection over those systems rather than another authority.

## 9. Chronicle and reports

Append-only Chronicle events and report directories made work auditable, but also introduced another memory layer to synchronize.

**Carry forward the intent, simplify the mechanism**

For the MVP:

- Git history records policy/config evolution,
- tracker history records work coordination,
- PRs record review decisions,
- CI/evals record validation,
- `memory/` stores only reviewed reusable lessons.

Add a dedicated event store later only if a concrete cross-system query cannot be answered from these sources.

## 10. Validation and tests

Local Agent Workshop's most operationally successful pieces were deterministic validators, tests, CI, and fixtures.

**Carry forward strongly**

CAW ships with:

- configuration validation,
- deterministic planning,
- testable role selection,
- CLI smoke tests,
- CI from the first MVP.

If a governance rule can become a deterministic assertion, prefer that over prose alone.

## 11. Supervisor and Proxmox roadmap

The older roadmap planned a supervisor control plane, agent leases, budgets, tracing, retries, queues, App/MCP/A2A boundaries, and a Proxmox Workshop Node.

Many of those are legitimate distributed-systems concerns, but they were planned before a real supervisor was operating.

Current Codex and Symphony capabilities change the build-vs-buy boundary.

**CAW decision**

- Codex supplies the agent execution harness.
- Symphony supplies the continuous tracker-to-workspace staffing loop.
- CAW supplies organization, routing, procedures, business policy, and eval-driven learning.
- Proxmox is an optional future compute provider.

Do not reimplement the supervisor until a missing requirement is demonstrated.

## 12. What is retained

| Local Agent Workshop idea | CAW form |
|---|---|
| instruction spine | concise `AGENTS.md` + nearby docs |
| Skills | `.agents/skills/*/SKILL.md` |
| skill discovery | team role + skill routing |
| execution contract | tracker issue / work packet |
| agent roles | configurable Team TOML |
| HyperKanban role/risk dimensions | role definitions + tracker labels |
| quality analysis | risk-proportional reviewer/evals |
| human approval boundaries | business consequence gates |
| verification | deterministic CLI validation + tests + CI |
| self-improvement | evidence-triggered proposals |
| supervisor roadmap | Codex + Symphony |
| Proxmox runtime | optional infrastructure adapter later |

## 13. What is intentionally absent from MVP

- custom project-state database,
- custom queue/broker,
- custom worktree manager,
- custom Chronicle event store,
- custom dashboard,
- large schema registry,
- Proxmox requirement,
- automatic issue creation after every procedure use,
- mandatory multi-stage ritual for trivial work,
- hard-coded model catalog.

## Success criterion

The product succeeds when this statement is true:

> A human can state a real objective, have the smallest appropriate agent team produce a high-quality reviewable result, and learn from the outcome with less human attention and context waste than before.

Everything else is secondary architecture.
