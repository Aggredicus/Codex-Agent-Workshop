---
name: orchestrate-team
description: Compile a goal into the smallest sufficient Codex Agent Workshop team, execute independent roles in parallel when the harness supports it, review the combined evidence, and integrate one bounded result.
---

# Orchestrate Team

Use this Skill when a task benefits from multiple professional perspectives or separable workstreams.

## Procedure

1. Read `AGENTS.md`, `WORKFLOW.md`, and the selected `teams/<team>/team.toml`.
2. Run:
   ```bash
   caw plan --team <team> --goal "<objective>"
   ```
3. Inspect the selected roles. Remove an optional role when its contribution is not plausibly worth its context/coordination cost.
4. Give each role:
   - the objective,
   - its mandate and challenge function,
   - only its listed/relevant context,
   - required output,
   - evidence expectations,
   - stop/consequence boundaries.
5. If native subagents are supported, run independent work-wave roles concurrently.
6. Otherwise use the single-model fallback: execute roles sequentially and freeze a compact handoff after each role.
7. Reviewers inspect the combined specialist evidence; they do not merely endorse it.
8. The final integrator produces one coherent result with:
   - decision/deliverable,
   - evidence,
   - assumptions,
   - disagreements,
   - unresolved risks,
   - human decision or consequence gate,
   - next action.

## Handoff format

```text
role:
conclusion:
evidence:
assumptions:
risks:
artifacts:
open questions:
recommended next step:
```

## Efficiency rules

- Do not spawn every available role.
- Do not give every role the full repository.
- Do not paste full role transcripts into later roles when a compact evidence handoff suffices.
- Parallelize only genuinely independent work.
- Escalate compute/model class only when task difficulty or review evidence warrants it.

## Quality rules

- Roleplay is not evidence.
- A reviewer should identify defects, not optimize for agreement.
- High-risk outputs must not be self-approved by the producing role.
- Preserve material dissent in the integration packet.

## Stop

Stop before a human-gated consequence described in `WORKFLOW.md` or the team policy.
