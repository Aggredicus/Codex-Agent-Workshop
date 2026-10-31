# Reciprocal skill exchange — draft operating policy

## Purpose
CAW's public contributor gateway supports three distinct invitations:
1. **Offer help:** a volunteer asks for a scoped open-source contribution to an Aggredicus project.
2. **Request help:** a public-source maintainer asks whether a documented CAW/portfolio capability could help their own project.
3. **Propose an exchange:** two humans (possibly using agents) discuss independently scoped contributions in both directions.

These are requests for discussion. Nothing automatically creates a reciprocal obligation, employment relationship, schedule, payment, license grant, or repository permission.

## Authority and identity
- Each project has an identified human maintainer who approves scope and code integration.
- Agent submissions must identify the responsible human/operator's public GitHub handle. Agents cannot independently bind a human, accept obligations, or grant themselves access.
- Contributors choose their level of involvement; no time tracking, leaderboard, peer-pressure, or traded-hour credits are introduced.
- AI-generated contributions must be reviewed for correctness, license provenance, and any relevant disclosure policy.

## Skill catalog
The machine-readable catalog at `docs/volunteer/offered-skills.json` lists **candidate support areas inferred from documented project work**, not independently verified human skill qualifications or guaranteed availability. Never claim all listed skills are personally mastered, always available, or suitable for every third-party project.

## Request process
1. Submit a public `Request open-source coding help` form or `Propose a skill trade` form. Provide only public repository links and a small, testable problem.
2. Maintainer screens for license, scope, effort, risk, existing commitments, and openness of the project.
3. If a possible fit exists, identify separate source-of-truth issues (and reviewers) in the relevant repositories. Explicitly document the contributions, acceptance criteria, and applicable licenses.
4. Work proceeds on forks or restricted branches, with no shared credentials or default-branch write access. Protect unrelated user data.
5. Record each accepted deliverable using source code, tests, and PR review evidence. Close the issue with a summary; do not assume reciprocal work was 'owed'.

## Commercial and legal boundaries
- Public forms solicit open-source collaboration, not free work in a for-profit company's ordinary business.
- Requests involving private customer work, contractual service exchanges, compensated time, or business deliverables require separate explicit arrangements and qualified legal/tax review.
- **Barter can create tax obligations even when no money changes hands**; see https://www.irs.gov/publications/p525 . Avoid making enforceable quid-pro-quo promises by issue comment alone.
- Originality and provenance must be verified; the absence of a separate agreement does not guarantee clear IP ownership.
- Maintain a code of conduct, moderation expectations, and a disclosure path for security issues before scaling outreach.

## Next steps before publishing
- Confirm the offering descriptions and scope with the account owner.
- Add an explicit availability signal to each offer only after confirmation; default is 'by discussion.'
- Confirm GitHub Issues is enabled on CAW and template forms are available on the default branch.
- Review profile README draft, contributor handbook and public links. Publish only after final approval and verification.
