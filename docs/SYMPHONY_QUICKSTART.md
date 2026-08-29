# Symphony Quickstart

Codex Agent Workshop is usable without Symphony. Symphony becomes valuable when you want a continuously running service to keep eligible tracker tasks staffed with Codex sessions.

## Current reference boundary

OpenAI's Symphony v1 specification currently defines `tracker.kind: linear`. CAW itself is tracker-neutral.

If you use GitHub Issues today, you can:

- use them manually as CAW work packets,
- have Codex work them interactively,
- use a Symphony implementation/adapter that supports GitHub,
- or mirror your continuously dispatched work into Linear.

Do not assume the reference v1 Linear adapter consumes GitHub labels directly.

## 1. Install CAW in the project workspace

```bash
python -m pip install -e ".[dev]"
caw validate
```

Install/authenticate Codex separately and confirm:

```bash
codex --version
codex app-server --help
```

## 2. Prepare Linear

Create/select a Linear project for the work you want Symphony to staff.

Set the API key in the environment rather than committing it:

```bash
export LINEAR_API_KEY="..."
```

## 3. Create a Symphony workflow

Copy:

```text
symphony/WORKFLOW.linear.example.md
```

to the workflow path your Symphony implementation uses, then replace:

```yaml
project_slug: CHANGE_ME
```

with the Linear project slug.

The example deliberately uses `$LINEAR_API_KEY`; do not paste the secret into version control.

## 4. Tune concurrency

Start conservatively:

```yaml
agent:
  max_concurrent_agents: 2
```

Raise it only after observing:

- model rate limits,
- local CPU/RAM,
- workspace/tool contention,
- review capacity,
- whether the tasks are truly parallelizable.

CAW's *internal* team parallelism and Symphony's *task-level* parallelism are separate layers. A high number in both can multiply concurrency quickly.

## 5. Make tasks agent-ready

A tracked objective should include:

```text
objective
inputs
outputs
evidence
acceptance criteria
stop conditions
non-goals
team (optional; default solo-llc)
human-gated consequence
```

The repository's GitHub Agent Task issue template demonstrates the same work-contract grammar even if Linear is the active Symphony tracker.

## 6. Let the repo compile the team

Inside each task workspace, the workflow asks the worker to run:

```bash
caw plan --team <team> --goal "<objective>" --mode symphony
```

The team compiler selects the minimum useful roles, their context hints, skills, compute classes, and review roles.

## 7. Human review remains a valid terminal handoff

A successful agent run does not have to mean the real-world business consequence is complete.

For example, the system can finish:

- the client proposal but not send it,
- the invoice analysis but not move money,
- the contract review packet but not accept terms,
- the marketing campaign but not publish it,
- the ecological design but not claim an unverified engineering conclusion.

That is the intended boundary.

## Official references

- https://openai.com/index/open-source-codex-orchestration-symphony/
- https://openai.com/index/unlocking-the-codex-harness/
