# Find Your Place — maintainer operating procedure

Status: **draft**. This page is not a published call for volunteers until approved, merged, and linked from the profile.

## Purpose
Provide a low-friction, privacy-preserving way for a visitor to compare self-reported skills with candidate contributor opportunities across the Aggredicus public open-source repositories.

## Current architecture
- `index.html` is a **single-file**, offline-capable, dependency-free, mobile-responsive matcher.
- Its embedded `<script id="catalog" type="application/json">` holds the candidate catalog.
- Candidate entries are **proposals**, not verified tasks or promises of available slots.
- Matching uses explicit tag overlap, not inferred personal traits, CV scraping, or automated profiling.
- All entries are shown before any skills are chosen. No selection is saved or transmitted.
- Visitors navigate to an existing repository and can open a *public* interest issue only once the template is available on the default branch.
- There is no contact form, backend, messaging service, telemetry, or permissions delegation.

## Publication gates
1. Confirm the intended volunteer scope is genuinely open-source community work, not unpaid labor for a commercial entity. Get qualified employment-law advice for uncertain boundaries.
2. Review each target repository's licensing and contribution process. Missing licenses are a blocker for inviting code contributions to that repository.
3. Turn the most promising proposed areas into small, current, maintainable GitHub issues with acceptance criteria and labels (`help wanted` or `good first issue` as appropriate). Keep the skill catalog aligned with verified issues.
4. Merge the reviewed change to `main`; publish from `main/docs` in GitHub Pages if desired (site root `/volunteer/`). Do not assume Pages is enabled until confirmed.
5. Create a public profile README repository `Aggredicus/Aggredicus` after approval, and adapt `docs/PROFILE_README_DRAFT.md`. Link to the verified live site.
6. Consider an account-level public `Aggredicus/.github` defaults repository for contribution guides, conduct, security and issue templates—but do not create it automatically.
7. Use optional public issue responses only; never request personal contact information, government identifiers, or sensitive work samples.
8. Monitor new issues for prompt acknowledgement. Never advertise an opportunity that no maintainer is available to review.

## Maintenance and evidence
For each proposed opportunity record: define source repository, skill tags, level, a narrow potential first contribution, and candidate status. On approval, add canonical issue references and reviewer/owner assignments in the tracker before changing its status to open.

Avoid fabricated urgency, skill scores, automated contributor vetting, or claims that the visitor's skills have been independently verified. Humans can help across skill gaps not in the inventory.

## Acceptance checks
- `pytest -q` runs syntax/catalog safety checks in `tests/test_volunteer_gateway.py`.
- Test Chrome and Firefox desktop, Android browser, keyboard focus, no-JavaScript fallback, screen-reader labels, and offline `file://` open before publication. These are **not** certified by static tests.
- Manually verify all links, licenses, labels, and Pages deployment after merge.
