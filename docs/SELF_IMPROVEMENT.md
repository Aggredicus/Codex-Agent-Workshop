# Evidence-Triggered Self-Improvement

The workshop should improve from real work without turning every run into administrative work or allowing agents to rewrite their own rules unchecked.

## Principle

```text
observe cheaply
evaluate consistently
propose changes only when evidence warrants them
test the smallest useful change
keep consequential policy changes reviewable
```

## Run record

When the harness can provide them, capture:

```text
team
objective
roles selected
roles actually useful
model class / actual model
context references
input/output token usage
latency
tool failures
review findings
human corrections
rework count
acceptance / rejection
customer or stakeholder feedback
```

Missing telemetry should not block useful work. Add instrumentation when it answers a decision.

## Improvement triggers

Create an improvement proposal when one or more of these is meaningful:

- the same human correction recurs,
- the same reviewer finding recurs,
- role routing repeatedly selects an irrelevant role,
- a needed specialist is repeatedly missing,
- a context bundle is repeatedly insufficient or wasteful,
- token use regresses materially without a quality gain,
- a tool/connector repeatedly fails in a reusable way,
- output fails an evaluation that should have been predictable,
- a customer/stakeholder correction reveals a generalizable lesson,
- a safety/risk boundary was unclear,
- an acceptance criterion cannot be evaluated reliably.

Do **not** create an improvement proposal merely because a run happened.

## Diagnosis order

Before changing architecture, ask:

1. Was the task underspecified?
2. Was the relevant context missing or excessive?
3. Was the wrong role selected?
4. Was the role mandate ambiguous?
5. Was a Skill missing or weak?
6. Was a tool unreliable?
7. Was the evaluation/rubric weak?
8. Only then: is planner/runtime/governance change justified?

This ordering favors small fixes.

## Change ladder

Prefer the lowest rung that fixes the measured problem:

```text
1. add/fix an eval or test
2. improve documentation/context
3. improve a Skill
4. refine a role
5. refine routing
6. add/change a tool
7. change runtime architecture
8. change governance
```

## Improvement proposal format

```markdown
# Improvement proposal

Problem:
Evidence:
Frequency / impact:
Hypothesis:
Smallest proposed change:
Expected quality effect:
Expected token/time effect:
Evaluation that would prove improvement:
Risk:
Rollback:
Human decision required:
```

## Evaluation dimensions

A useful optimization compares at least some of:

- acceptance rate,
- defect/reviewer finding count,
- human correction time,
- customer/stakeholder satisfaction when available,
- input/output tokens,
- latency,
- number of model turns,
- rework loops,
- tool errors,
- consequence-gate escalations.

Avoid optimizing a single number in isolation.

## Preventing self-reinforcement

The agent that proposes a material change should not be the sole judge of whether it worked.

Use one or more of:

- deterministic tests,
- a separate reviewer role,
- a before/after fixture,
- human review,
- blind comparison,
- repeated-run evidence.

High-risk policy changes remain human-reviewed.

## Memory hygiene

`memory/` is for reviewed, reusable knowledge—not raw transcripts.

Promote a lesson into durable memory when it is:

- likely to matter again,
- supported by evidence,
- concise enough to retrieve usefully,
- not secret/sensitive,
- not contradicted by a more authoritative source.

Expire or supersede stale lessons rather than accumulating conflicting instructions forever.
