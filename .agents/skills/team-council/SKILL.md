---
name: team-council
description: Run a structured multi-role business or design council that elicits independent positions, evidence, assumptions, and dissent before an integrator makes a decision.
---

# Team Council

Use this Skill when a decision materially benefits from conflicting professional incentives.

## Native multi-agent method

1. Give each selected role the same decision question plus its own mandate/context.
2. Ask for an **independent position before showing other roles' positions** to reduce anchoring.
3. Collect compact position packets.
4. Let roles inspect and challenge the other packets.
5. Give the evidence and challenges to the integrator.

## Single-agent fallback

A single model can simulate the council, but preserve independence:

1. execute Role A and freeze its position,
2. execute Role B without revising A,
3. continue for all roles,
4. then run a challenge round,
5. only then integrate.

## Position packet

```text
role:
position:
facts/evidence:
assumptions:
what would change my mind:
principal risk:
recommended action:
```

## Final council record

```text
decision:
agreed facts:
material disagreements:
assumptions still unresolved:
dissent worth preserving:
evidence:
human approval needed:
next owner/action:
```

## Rules

- Do not manufacture disagreement when roles genuinely converge.
- Do not manufacture consensus by smoothing over real dissent.
- Roleplayed professional viewpoints do not replace licensed/legal/financial/engineering review when one is actually required.
- Prefer factual challenge over personality theater.
