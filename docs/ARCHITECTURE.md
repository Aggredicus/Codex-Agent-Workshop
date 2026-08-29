# Architecture

Codex Agent Workshop (CAW) is intentionally small: it defines an organization and compiles goals into bounded work packets. It does not try to replace the execution harness, task tracker, Git, CI, or human judgment.

## Mental model

```text
Team TOML       = org chart + routing policy
caw             = deterministic task/team compiler
Skills          = reusable procedures
AGENTS.md       = short navigation map
WORKFLOW.md     = task lifecycle and Symphony-facing policy
Codex           = execution harness
Symphony        = continuous staffing supervisor
Task tracker    = project control plane
PR + CI         = code review and validation evidence
memory/         = reviewed, durable lessons
```

The repository is the durable operating manual. Model context is a temporary working set.

## Execution shape

A normal objective is compiled into four waves:

```text
1. PLAN
   coordinator / chief of staff
        |
        v
2. WORK
   specialist A ─┐
   specialist B ─┼─ independent work in parallel when possible
   specialist C ─┘
        |
        v
3. REVIEW
   critic / science / finance / risk / QA as relevant
        |
        v
4. INTEGRATE
   coordinator produces one decision or deliverable packet
```

A role is selected because the objective overlaps its mandate, not because the role exists. The default is the smallest sufficient team.

## One design, three execution modes

### Single-model

One capable model carries the roles sequentially. Each role receives only its context slice and leaves a compact handoff for the next role.

This is the universal fallback and makes the team definitions portable to harnesses that cannot spawn subagents.

### Native multi-agent

A capable harness such as Codex may execute independent work-wave roles concurrently in isolated contexts/workspaces, then invoke reviewers and the integrator.

Parallelism is a performance optimization, not a semantic requirement.

### Symphony

Symphony is the outer, continuous staffing loop. A tracker item becomes the unit of work. Symphony creates or reuses an isolated workspace, starts Codex, and gives the agent the repository-local workflow.

CAW sits inside that workspace:

```text
tracker issue
    |
    v
Symphony
    |
    v
isolated workspace
    |
    v
caw plan
    |
    +--> role packets / skills / context
    |
    v
Codex execution
    |
    v
evidence + tracker/PR update
```

CAW does not need its own duplicate queue or project-state database for the MVP.

## App Server seam

For interactive use, `caw prompt` is enough: it renders a compact orchestration prompt that Codex or another harness can execute.

A later adapter can use Codex App Server to create durable threads/turns, receive streaming events, surface approvals, and maintain bounded concurrency. The team compiler should remain independent of that transport.

## Context economy

The primary token-efficiency rule is **progressive disclosure**.

A role definition contains context path hints such as:

```toml
context = [
  "business/brand/",
  "business/offers/",
  "business/sales/"
]
```

The orchestrator should inspect those paths and load only the files required for the current task. It should not concatenate the entire repository into every agent prompt.

Compact handoffs are preferred to sharing full transcripts:

```text
role:
conclusion:
evidence:
assumptions:
open questions:
artifacts:
recommended next step:
```

## Model classes

Teams specify abstract compute classes rather than vendor model names:

- `fast` — classification, formatting, narrow retrieval, repetitive work.
- `balanced` — most research, drafting, and operational work.
- `deep` — difficult synthesis, architecture, adversarial review, consequential ambiguity.

Harness adapters map those classes to whatever models are currently available. This prevents business procedures from becoming obsolete every time the model catalog changes.

## Role design

Useful roles have a mandate and a productive bias. They should not be differently named clones.

For example:

```text
Sales:
  optimize conversion and customer value
  challenge unclear benefits and weak next actions

Ecological design:
  optimize site fit, resilience, and long-term function
  challenge unsupported site assumptions

Finance:
  optimize margin, cash flow, and scope discipline
  challenge underpricing and unfunded commitments

Quality reviewer:
  optimize truthfulness and deliverable quality
  challenge everybody
```

Structured disagreement is valuable only when roles have different responsibilities and are required to expose evidence and assumptions.

## Risk and human agency

Automation can prepare consequential work without automatically activating the consequence.

Examples that normally remain human-gated:

- sending external communications in the owner's name,
- signing contracts or accepting binding terms,
- moving money or initiating payments,
- filing taxes or regulatory/legal documents,
- using or changing live credentials,
- publishing to production,
- deleting irreplaceable data,
- making safety-critical engineering claims,
- releasing sensitive customer information.

The workshop should maximize work completed *up to* those boundaries.

## Learning

Every run may be logged cheaply. A run does not automatically deserve a new issue or policy change.

An improvement proposal is warranted when there is evidence such as:

- repeated human correction,
- repeated reviewer finding,
- measurable excess token or latency cost,
- recurring tool failure,
- missing or misleading context,
- wrong role selection,
- weak acceptance/evaluation score,
- customer feedback that reveals a reusable lesson.

See `docs/SELF_IMPROVEMENT.md`.

## Why Proxmox is not in the MVP

Proxmox can later host local models, runners, caches, databases, artifacts, or long-lived services. It is infrastructure, not the organizational model.

CAW should work identically with:

- hosted Codex,
- a single local model,
- a mixed cloud/local harness,
- or future Proxmox-hosted workers.

That separation lets the organization mature before committing to an infrastructure stack.
