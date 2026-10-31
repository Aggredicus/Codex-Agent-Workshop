---
name: skill-inventory
description: Build and verify a privacy-scoped, extensible repository capability inventory from approved Skill definitions and team references. Do not infer personal competence or publish private node identities.
---

# Skill Inventory

Use this skill when another agent or human asks to inventory documented capabilities, identify **candidate** skill coverage, compare public task requirements, or refresh the public skill inventory.

## Authority and scope

- The reviewed taxonomy at `skill-inventory/taxonomy.json` is authoritative for public skill IDs and mappings.
- The generator at `scripts/build_skill_inventory.py` examines only allowlisted `.agents/skills/*/SKILL.md` frontmatter `name` and role skill-ID references in `teams/*/team.toml`.
- It does **not** read people, personal files, machine serials, private tokens, Git commit authors, GitHub profiles, or general prose.
- `documented-in-repository` means a matching procedure exists, **not** that an individual or model is proficient. `not-observed` is an unknown, not a person's weakness.
- Physical nodes, agent-origin manifests and instance-specific skill assertions are LAW-only private data; do not add them to CAW public JSON.

## Procedure

1. Read `skill-inventory/taxonomy.json` and the task's target repository scope.
2. Run `python scripts/build_skill_inventory.py --check`; use `--write` only when an intentional, reviewed refresh is needed.
3. Validate that the JSON contains only allowlisted category IDs and repository Skill IDs, with no human names, emails, hostnames, IPs, tokens, or device identifiers.
4. Review any taxonomy changes for security, licensing and classification errors before writing public output. Add only reviewed mappings; unknown terms must not be guessed into a personal capability.
5. Run `pytest -q` (plus appropriate related tests), inspect the diff, and submit a PR for independent human review.
6. Match skills against open issues using evidence and explicit skill labels; never automatically grant privileges or bind a person to a task.

## Outputs

- `skill-inventory/inventory.json` as the generated public snapshot.
- A short report listing count of defined capability IDs, count with repository documentation, unknown/gaps **in repository evidence only**, and missing external verification.
- An explicit stop before publishing identity-linked or machine-sensitive data.

## Change and risk controls

Taxonomy schema is versioned. New categories can be added without changing the generator; source-to-category mappings need tests and review. A taxonomy or agent version update does not grant privileges. The separate local runtime is maintained in [Local Agent Workshop](https://github.com/Aggredicus/Local-Agent-Workshop).

Never use this skill to scrape people, grade applicants, deduce private characteristics, create automatic employment rankings, claim agent attestation, or bypass GitHub role and review policies.
