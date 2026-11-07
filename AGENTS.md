# 4FusionLab engineering instructions

This repository holds reusable, **read-only** CI building blocks and organization-level defaults. Product-specific instructions belong in each product repository.

## Language and product documentation
- For product README creation or edits, follow [Product README guidelines](README_GUIDELINES.md), including language parity and license verification.
- Write documents in English; maintain separate Russian versions of documentation. Intermediate working notes do not require translation.
- Discuss requirements and plans in Russian. Use English for Autodesk Fusion UI labels, stable API identifiers and public action input names.
- Maintain separate EN/RU user documentation where a product already has both. Never silently replace either language with spoilers or machine-generated placeholders.
- Respect existing product architecture, UX contracts, tests and CAD compatibility caveats.

## Git, CI and releasing
- Prefer a small, reviewed PR for CI/publishing changes. Do not force-push or amend public history. Keep direct main pushes possible where repository permissions allow them.
- Do not manually create release tags. A push or PR merge to `main` may publish **only when shipped runtime inputs have changed since the last published Release**. A docs-only push can recover an earlier failed runtime release, but must never independently create one. See [`RELEASE_RECOVERY.md`](RELEASE_RECOVERY.md).
- Preserve each repository's `.github/release-paths.txt` as its reviewed release-eligibility allowlist. Pure README, docs, test, workflow, policy and AGENTS.md changes must not create a GitHub Release.
- GitVersion.Tool is pinned to **6.8.2**. Full Git history is required. Published tags, releases and uploaded assets are immutable; never retarget tags, clobber artifacts or downgrade a prerelease to Stable.
- Core shared Actions live at `.github/actions/` and must be pinned by their exact commit SHA in consuming projects. Do not reference the moving `main` branch in production release jobs.
- Pin first-party `actions/*` usages to the exact reviewed SHAs in [`ACTIONS_PINS.md`](ACTIONS_PINS.md). Verify upstream tags before updating; do not use floating major-version tags in product workflows.
- Only publishing jobs need `contents: write`; package tests, metadata inspection and PR jobs run with least-privilege read permissions.
- A passing offline build or Python test **does not** imply Autodesk Fusion CAD acceptance. Preserve native platform evidence and security/compatibility gates.

## Quality
- Test common Actions with `python -m unittest discover -s .github/tests -v` and the Shared release platform checks workflow.
- For changed Actions, first merge a tested platform PR, then migrate consumers in separate PRs with green project CI. Avoid changing product runtime sources as part of CI migration.
- Before replacing product packaging commands, verify ZIP contents, manifest version, SHA-256, notes, and OS-platform differences for that product.
- Never place user credentials, secrets, personal CAD files, machine-specific paths or proprietary material into this public repository.

## Compatibility
- Preserve stable Fusion manifest UUIDs, command IDs, product names, platform-specific assets, supported OS metadata and each repo's installation format.
- Project-level `AGENTS.md` supplements these common expectations and remains authoritative for project-specific API/geometry/UX constraints.
