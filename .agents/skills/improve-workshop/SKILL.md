---
name: improve-workshop
description: Turn repeated or measurable run evidence into the smallest testable improvement proposal for context, Skills, roles, routing, tools, runtime, or governance without silently changing consequential policy.
---

# Improve Workshop

Read `docs/SELF_IMPROVEMENT.md` first.

## Trigger gate

Do not create work merely because a run occurred.

Continue only when there is substantive evidence: repeated correction, reviewer recurrence, cost regression, wrong routing, missing context, tool failure, weak eval, customer feedback, or a safety/governance ambiguity.

## Diagnose in this order

1. task specification,
2. context selection,
3. role selection,
4. role mandate,
5. Skill/procedure,
6. tool/connector,
7. evaluation,
8. planner/runtime,
9. governance.

Prefer the earliest layer that plausibly explains the problem.

## Propose the smallest change

Prefer:

```text
test/eval
→ context/docs
→ Skill
→ role
→ routing
→ tool
→ runtime
→ governance
```

## Required proposal

```text
problem:
evidence:
frequency/impact:
hypothesis:
smallest proposed change:
expected quality effect:
expected token/time effect:
evaluation:
risk:
rollback:
human decision required:
```

## Verification

A material change should be judged by a different signal than the proposing agent alone: deterministic test, separate reviewer, before/after fixture, human comparison, or repeated-run evidence.

## Forbidden

- Do not automatically adopt your own governance change.
- Do not generate recursive improvement issues with no evidence.
- Do not rewrite durable memory from a single weak anecdote.
- Do not optimize token count while ignoring quality/rework.
