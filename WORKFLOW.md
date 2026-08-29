# Workshop Workflow

This file is the versioned workflow policy for tracked agent work. It is intentionally compatible with a Symphony-style supervisor: the tracker owns task lifecycle; a Codex workspace executes one eligible task; the repository owns the rules.

When a Symphony-compatible renderer supplies issue variables, treat this as the current task:

```text
issue: {{ issue.identifier }}
title: {{ issue.title }}
description: {{ issue.description }}
attempt: {{ attempt }}
```

When these placeholders are not rendered, use the objective supplied directly by the human or harness.

> OpenAI's Symphony v1 specification currently defines a Linear tracker adapter. The GitHub labels below are CAW's recommended semantics for manual/GitHub-compatible orchestration; use equivalent Linear states or a GitHub-capable Symphony adapter for continuous dispatch.

## 1. Eligibility

A task is eligible when it is open, actionable, not dependency-blocked, and explicitly marked ready by the configured tracker policy.

For GitHub-based coordination, the recommended MVP labels are:

```text
agent:ready
agent:active
agent:review
agent:blocked
agent:human
```

An external Symphony implementation may map equivalent tracker states to these semantics.

## 2. Arrival

For each eligible task:

1. create or reuse an isolated workspace/worktree;
2. read `AGENTS.md`;
3. identify the requested team (default `solo-llc`);
4. read `teams/<team>/team.toml`;
5. compile the objective with `caw plan`;
6. begin only if required context is available and the task is within the role/risk boundary.

## 3. Plan

Compile the objective into:

- coordinator/planning assignment,
- minimum sufficient specialist work wave,
- independent review wave,
- integration/handoff assignment.

Do not spawn every role. Do not parallelize dependencies.

When the task names a role or procedure explicitly, honor it unless that would violate a risk or permission boundary.

## 4. Execute

### Native multi-agent mode

When the harness supports subagents/worktrees:

- delegate independent assignments in the same work wave in parallel;
- keep role context isolated;
- give each worker only its role packet plus task-specific inputs;
- require a compact structured handoff;
- let the coordinator synthesize, resolve conflicts, and request targeted follow-up.

### Single-agent fallback

When only one model is available:

- preserve the same plan;
- execute roles sequentially;
- reset the active role mandate between assignments;
- maintain a compact shared decision log;
- do not let a role silently modify another role's conclusions—record disagreements.

## 5. Council / disagreement

Use `.agents/skills/team-council/SKILL.md` when a decision benefits from conflicting professional incentives.

Council dialogue is a reasoning artifact, not authority. End with:

```text
facts agreed
disagreements
assumptions
decision
dissent / unresolved risk
evidence needed
owner of next action
```

## 6. Evidence

A task is ready for review only when its handoff states:

```text
objective
roles used
outputs produced
evidence / source paths
checks performed
assumptions
known limitations
risks
recommended next action
human decision needed
```

Do not claim completion from prose confidence alone.

## 7. Human-gated consequences

Agents may prepare, simulate, draft, calculate, research, and stage work aggressively.

Stop before unapproved live effects involving:

- payments or financial transfers,
- binding contracts,
- legal or regulatory filings,
- tax submissions,
- credential or access changes,
- destructive infrastructure/data actions,
- sensitive customer-data disclosure,
- public production changes with material business risk,
- other task-specific high-risk consequences.

## 8. Review and tracker transition

Recommended lifecycle:

```text
ready -> active -> review -> done
                  \-> blocked
                  \-> human
```

A Symphony supervisor should keep an eligible task staffed while it is `active`, restart recoverable failures within its retry policy, and stop the run when the tracker makes the task ineligible.

The coding/working agent may update task comments, PR links, and tracker state when the runtime grants those tools. The supervisor should remain the scheduler, not the business-domain authority.

## 9. Improvement closeout

After the outcome is evaluated:

- record useful metrics and human corrections;
- update `memory/` only with durable lessons;
- create an improvement proposal only if there is actionable evidence;
- test proposed role/skill/routing changes against representative tasks before adoption.

Repeated success with no meaningful lesson requires no administrative artifact beyond the normal run record.
