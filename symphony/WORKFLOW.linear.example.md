---
tracker:
  kind: linear
  api_key: $LINEAR_API_KEY
  project_slug: CHANGE_ME
  active_states:
    - Todo
    - In Progress
  terminal_states:
    - Closed
    - Cancelled
    - Canceled
    - Duplicate
    - Done
polling:
  interval_ms: 30000
workspace:
  root: ~/codex-agent-workshop-workspaces
agent:
  max_concurrent_agents: 4
  max_turns: 20
codex:
  command: codex app-server
---

You are working on tracked objective {{ issue.identifier }} — {{ issue.title }}.

Issue description:

{{ issue.description }}

Attempt: {{ attempt }}

Read `AGENTS.md`, then read the repository `WORKFLOW.md` and the appropriate `teams/<team>/team.toml`.

Treat the issue as the objective and execution contract. If it identifies a CAW team, use it; otherwise default to `solo-llc`.

Run:

```bash
caw plan --team <team> --goal "<issue title and objective>" --mode symphony
```

Then execute the compiled role plan using `.agents/skills/orchestrate-team/SKILL.md`.

Requirements:

- use the minimum sufficient roles;
- load role-specific context progressively;
- parallelize only independent specialist work;
- validate claims and artifacts before handoff;
- preserve material reviewer dissent;
- keep business consequence gates in `WORKFLOW.md`;
- update the tracker/PR with concise evidence if the runtime provides those tools;
- end in a human-review/blocked state rather than activating an unapproved consequential action.

Return an owner/reviewer-ready handoff with outputs, evidence, checks, assumptions, risks, and the exact next decision.
