# Recovering missed automatic releases

[Русская версия](RELEASE_RECOVERY.ru.md)

## Problem

A push can modify a shippable runtime file while CI or the publishing job fails.
The next push may contain only README, tests, or workflow changes; a detector
limited to `github.event.before..github.sha` would permanently miss the earlier
eligible change unless another runtime file were modified.

## New opt-in rule

On a **push to `main`**, the shared `runtime-changes` Action can query the
repository's GitHub Releases, resolve the most recently **published** Release
with ZIP assets whose version tag is an ancestor of the current commit, and
compare its tagged commit against `github.sha` using `git diff --no-renames`.

- If there are eligible runtime paths in that cumulative diff, the existing
  CI and publication gates run; no manual tag is required.
- If there are none, skip publication even if documentation or workflow files
  changed.
- If there has never been a published ZIP Release, fall back to the **current
  push range**. This preserves the original first-release behavior.
- Ignore drafts, non-version tags, and Releases without ZIP assets.
- Release tags and assets remain immutable; do not overwrite or move them.
- If GitHub API access fails, a published tag cannot be found locally, or
  no published tag is an ancestor of the current commit, **fail closed**.
  Otherwise a publication could silently be skipped.
- A docs-only push can now *retry a previously missed release*, but it does
  not create a release on its own.

A published Release with a ZIP is used as the historical checkpoint. Some
older Releases (for example RuEn 1.0.0) have no separate SHA-256 sidecar.
New release artifacts continue to be validated by the product's existing
ZIP/manifest/SHA-256 gates.

## Consumer workflow

Always pin the **merged platform commit SHA** in consumer workflows. The
new mode is intentionally opt-in to preserve old behavior for projects that
have not migrated.

```yaml
- name: Detect previously unpublished runtime changes
  uses: 4FusionLab/.github/.github/actions/runtime-changes@<REVIEWED_PLATFORM_SHA>
  with:
    before: ${{ github.event.before }}
    after: ${{ github.sha }}
    paths-file: .github/release-paths.txt
    recover-unpublished: 'true'
    token: ${{ github.token }}
```

Use `permissions: contents: read` for the classification job and `fetch-depth: 0`
for checkout; preserve `contents: write` only on the actual publishing job.

**Critical:** The release workflow must run on *every push to main*. A
workflow-level `push.paths` filter prevents docs-only push recovery, even if
the classifier is correct. Preserve narrow PR filters where practical, but
remove push path filters in a migrated release workflow.

## Tests

- Platform tests include GitHub API pagination/auth failure, malicious tags,
  published ancestry, drafts, no-release fallback, and missed-release retry.
- Product PR CI continues to validate the full build before a release.
- Verify post-merge behavior with both `Release eligible: true` (unpublished
  runtime changed) and `Release eligible: false` (no unpublished inputs).
- Never create tags or Releases from a PR or manual workflow dispatch.
