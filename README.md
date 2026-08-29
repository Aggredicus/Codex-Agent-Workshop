# Codex Agent Workshop

**Codex Agent Workshop (CAW)** is a small, repo-native operating system for building and running agent teams.

It is designed around a simple idea:

> Define the organization in the repository, compile goals into bounded work packets, let the harness execute them, and use evidence to improve the system.

The MVP supports three execution styles from the same team definition:

1. **Single-agent loop** — one model rotates through the selected roles in sequence.
2. **Multi-agent harness** — independent role assignments can run in parallel in Codex or another harness with subagents/worktrees.
3. **Symphony-style orchestration** — a supported issue tracker is the outer control plane; each eligible task gets a durable workspace and Codex run until it reaches a review or stop state. OpenAI's Symphony v1 reference spec currently defines a Linear tracker adapter.

The first general-purpose example is a **solo LLC operating team**. A second, richer example models **Permaculture Works LLC**.

## Why this repo exists

The previous Local Agent Workshop proved several useful ideas—short cold-start instructions, skills, evidence-backed tasks, risk boundaries, deterministic selection, and reviewable self-improvement—but it accumulated orchestration concepts faster than the runtime that would execute them.

CAW starts over with the runtime assumptions that now exist:

- Codex supports parallel agent workflows and isolated worktrees.
- Codex Skills provide reusable repository-local procedures.
- Codex App Server exposes the Codex harness programmatically.
- Symphony demonstrates an issue-tracker-as-control-plane pattern for continuously running coding agents.
- The same organizational model should still work when only one model is available.

See `docs/LOCAL_AGENT_WORKSHOP_ANALYSIS.md` for the migration analysis, `SPEC.md` for the new architecture, and `docs/SYMPHONY_QUICKSTART.md` for continuous orchestration setup.

## Quick start

Requirements: Python 3.11+.

```bash
python -m pip install -e ".[dev]"
caw doctor
caw teams list
caw validate
```

Generate a compact plan:

```bash
caw plan   --team permaculture-works   --goal "Prepare a client permaculture concept design, planting strategy, estimate, and review packet"
```

Generate a prompt you can paste directly into Codex, Cursor, or another agent harness:

```bash
caw prompt   --team permaculture-works   --mode multi   --goal "Prepare a client permaculture concept design, planting strategy, estimate, and review packet"
```

For a single-model fallback:

```bash
caw prompt   --team permaculture-works   --mode single   --goal "Prepare a client permaculture concept design, planting strategy, estimate, and review packet"
```

Create a new team:

```bash
caw init-team my-studio --name "My Studio"
caw validate --team my-studio
```

Then edit `teams/my-studio/team.toml`.

## Repository map

```text
AGENTS.md                         short agent-facing map
WORKFLOW.md                       Symphony/task lifecycle policy
SPEC.md                           harness-neutral orchestration specification

teams/
  solo-llc/team.toml              generic solo entrepreneur proof of concept
  permaculture-works/team.toml    Permaculture Works proof of concept

.agents/skills/                   Codex/Agent Skills
src/codex_agent_workshop/         deterministic compiler/CLI
docs/                             architecture and operating guidance
symphony/                         concrete Symphony workflow example
memory/                           durable lessons and improvement proposals
tests/                            mechanical guarantees
```

## Core commands

```text
caw doctor
caw teams list
caw team show <team>
caw validate [--team <team>]
caw plan --team <team> --goal "..." [--mode auto|single|multi|symphony] [--json]
caw prompt --team <team> --goal "..." [--mode auto|single|multi|symphony]
caw init-team <slug> --name "..."
```

## Design rules

- **Map, not manual:** keep `AGENTS.md` small and point to deeper sources.
- **Goals, not micromanagement:** define objectives, constraints, evidence, and stop conditions; let capable agents reason inside those boundaries.
- **Minimum sufficient team:** route only the roles useful for the current goal.
- **Progressive disclosure:** each role receives only its relevant context paths and skills.
- **Parallelize only independence:** role assignments in the same work wave must not depend on one another.
- **Evidence before completion:** every assignment returns a compact handoff with claims, evidence, blockers, and next actions.
- **Separate execution from approval:** high-consequence business actions and high-risk repository changes require explicit human approval.
- **Learn from signal, not ritual:** log runs cheaply; propose system changes only when evidence warrants them.
- **Harness independence:** organization definitions should survive changes in model or runtime.

## Current MVP boundary

This repository does **not** bundle or reimplement the full Symphony service. Instead it provides the repository contract Symphony needs: a stable `WORKFLOW.md`, team definitions, deterministic work-packet generation, review/stop semantics, and a clear Codex App Server integration seam.

Likewise, Proxmox is not required. Local or remote infrastructure can later become a runtime provider without changing the organization model.

## Safety

The workshop may prepare business actions, drafts, analyses, code changes, and proposed updates autonomously. By default it must stop before consequential live effects such as:

- sending external communications without an approved communication policy,
- executing payments or financial transfers,
- filing taxes or legal/regulatory documents,
- accepting contracts,
- exposing customer-sensitive data,
- changing production credentials or access,
- destructive infrastructure actions,
- merging high-risk changes without required review.

The point is to automate preparation and routine execution aggressively while preserving deliberate approval at real-world consequence boundaries.
