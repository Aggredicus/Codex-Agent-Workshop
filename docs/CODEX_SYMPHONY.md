# Codex and Symphony Integration

Codex Agent Workshop treats OpenAI's Codex and Symphony as execution infrastructure rather than embedding their implementation details into business procedures.

## The division of responsibility

```text
CAW
  organization, roles, Skills, routing, context policy, risk, evaluations

Codex
  reasoning + tool-using execution harness

Codex App Server
  programmatic harness surface for durable orchestration clients

Symphony
  continuous tracker -> isolated workspace -> Codex staffing loop

Tracker
  objectives, status, priority, dependencies, human coordination
```

## Official references

- Codex: https://openai.com/codex/
- Harness engineering: https://openai.com/index/harness-engineering/
- Symphony: https://openai.com/index/open-source-codex-orchestration-symphony/
- Codex App Server: https://openai.com/index/unlocking-the-codex-harness/

These are external capabilities. The repository should not copy their implementation.

## Mode 1: pasteable single-agent prompt

This is the minimum universal mode:

```bash
caw prompt --team solo-llc \
  --goal "Review our current lead pipeline and propose the next five actions" \
  --mode single
```

Give the result to Codex, Cursor, ChatGPT, or another capable harness.

One model plays each selected role sequentially and preserves role boundaries through structured handoffs.

## Mode 2: interactive native multi-agent

```bash
caw prompt --team permaculture-works \
  --goal "Prepare a client concept design with planting strategy and cost estimate" \
  --mode multi
```

A harness that can spawn agents should:

1. run the planning wave,
2. start independent specialist roles concurrently,
3. collect compact handoffs,
4. run reviewer roles over the combined evidence,
5. let the integrator produce the final packet.

Do not spawn agents solely because concurrency is available. Parallelize only independent work whose expected value exceeds coordination cost.

## Mode 3: Symphony

For continuous work, keep objectives in the task tracker and use repository `WORKFLOW.md` as the policy an arriving worker follows.

Suggested issue labels:

```text
agent:ready
agent:active
agent:review
agent:blocked
agent:human
```

An agent-ready issue should contain the work contract:

```text
objective
inputs
outputs
evidence
acceptance criteria
stop conditions
non-goals
risk / human-gated consequence
```

Symphony can continuously select eligible work and create isolated workspaces. Inside each workspace the worker runs `caw plan` or follows `caw prompt`.

This deliberately avoids a second CAW-specific queue.

## Mode 4: App Server adapter

A future `caw serve` or supervisor adapter can use Codex App Server when direct programmatic orchestration is worth the additional code.

Responsibilities of that adapter would include:

- starting/resuming Codex threads,
- starting turns with the correct work packet,
- consuming streamed item events,
- surfacing approval requests,
- correlating task IDs to threads/workspaces,
- enforcing bounded concurrency,
- recording cost/eval data.

It should **not** own the business organization. That stays in Team TOML and Skills.

## Tracker-neutral design

The repository includes a GitHub issue template because GitHub is a convenient coordination surface for the project. OpenAI's Symphony v1 specification currently defines a Linear tracker adapter, so continuous reference-Symphony dispatch should use Linear or a Symphony implementation with a GitHub adapter.

Team TOML and the deterministic compiler do not depend on either tracker. A tracker adapter only needs to map tracker records to the work contract.

See `docs/SYMPHONY_QUICKSTART.md` and `symphony/WORKFLOW.linear.example.md`.

## Business work is not always a PR

Many useful solo-business objectives end in:

- a client deliverable,
- a research brief,
- a proposal draft,
- a spreadsheet,
- a marketing campaign,
- a meeting packet,
- a site design,
- an operations checklist.

The review boundary for those tasks may be a human-facing artifact rather than a code PR.

The invariant is **evidence before consequence**, not “everything must be code.”

## Token and compute efficiency

CAW controls cost at five points:

1. **Role sparsity** — select the minimum sufficient roles.
2. **Context sparsity** — load role-specific paths, not the whole repo.
3. **Parallelism** — parallelize only independent work.
4. **Model class routing** — use `fast`, `balanced`, or `deep` by cognitive demand.
5. **Handoff compression** — transmit conclusions/evidence/assumptions, not full conversations.

Cost optimizations should be evaluated against output quality and rework. Cheap first-pass work that causes expensive correction is not efficient.

## Worktree responsibility

Do not build a second worktree manager into CAW while Codex/Symphony already provide isolated workspace concepts. CAW may annotate a plan with concurrency constraints, but the harness owns process/workspace lifecycle.

## Safety

A continuous supervisor increases throughput; it must not increase authority.

Symphony/Codex workers may progress a task up to explicit consequence gates. External sends, payments, binding commitments, filings, sensitive disclosures, destructive actions, and similarly consequential operations should remain human-governed unless the organization owner deliberately configures a narrower approved automation boundary.
