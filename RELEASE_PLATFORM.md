# Shared Release Platform

Central, reusable Actions for 4FusionLab repositories. Source: [4FusionLab/.github](https://github.com/4FusionLab/.github).

## Compatibility and rollout

| Action | Purpose | Required context |
| --- | --- | --- |
| `.github/actions/resolve-version` | GitVersion.Tool **6.8.2**, returns numeric version or SemVer | Complete checkout (`fetch-depth: 0`) |
| `.github/actions/runtime-changes` | Compare the full push range to `.github/release-paths.txt` | Full checkout, `before` and `after` commit SHA |
| `.github/actions/release-notes` | Use reviewed version notes or generate from history | Full checkout and writable `runner.temp` file |
| `.github/actions/verify-archive` | Validate package ZIP, SHA-256, optional Fusion manifest and nonempty notes | Built ZIP(s) and checksum files |

**Pin the action reference to the exact merged platform commit SHA**, not `@main` or a mutable tag. Open a separate consumer PR after the platform tests pass.

### Read-only release gating example

```yaml
- uses: actions/checkout@<approved-immutable-sha>
  with:
    fetch-depth: 0
    persist-credentials: false
- id: changes
  uses: 4FusionLab/.github/.github/actions/runtime-changes@<approved-platform-sha>
  with:
    before: ${{ github.event.before }}
    after: ${{ github.sha }}
    paths-file: .github/release-paths.txt
```

A product publishes only on `push` to `main` after its existing tests, build, notes and archive verification pass **and** the runtime-changes Action returns `release=true`. Skip publishing for PR, `workflow_dispatch` and documentation-only changes.

### Safety contract
- All composite Actions here are **read-only** and create no tags, GitHub Releases or Pages deployments. Final GitHub Release publication stays in the product repository to preserve its acceptance gates, channel semantics and packaging.
- No `contents: write` permission is granted by these Actions.
- A previously published version or mismatched immutable Git tag must never be overwritten.
- Changing tests or docs alone must not create releases. Runtime changes, including additions, deletions and renames, do.
- Do not assume that a successful CI ZIP build is proof of a native Fusion CAD integration test.

### Execution model

Repositories keep existing Linux/macOS/Windows CI matrices, Fusion acceptance checks, distribution builders and publishing gates. Centralized Actions only replace duplicated version resolution, path filtering, notes generation and archive validation.

Platform maintenance: add regression tests in `.github/tests`, pass `.github/workflows/platform-tests.yml`, merge to the platform repository, pin the new SHA in consumer PRs, verify all existing checks, and only then merge consumers.
