# Official GitHub Actions pins

[Русская версия](ACTIONS_PINS.ru.md)

This file is the 4FusionLab source of truth for first-party GitHub Actions used in CI, add-in packaging and (manual) GitHub Pages publishing. Check the upstream repository tag ref before changing any SHA. Pin to an immutable **40-character commit SHA**, not `@vN`, `@main` or an abbreviated hash.

| Action | Reviewed version | Immutable commit SHA |
| --- | --- | --- |
| `actions/checkout` | `v7.0.1` | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/setup-python` | `v7.1.0` | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` |
| `actions/setup-node` | `v6` | `249970729cb0ef3589644e2896645e5dc5ba9c38` |
| `actions/upload-artifact` | `v7.0.2` | `cf430e030ddbb5b0abf93d22962f4752f3646cd9` |
| `actions/download-artifact` | `v8.0.2` | `9000827ccba6bdab643e8b6fd33ac0654aef8333` |
| `actions/configure-pages` | `v5` | `983d7736d9b0ae728b81ab479565c72886d7745b` |
| `actions/upload-pages-artifact` | `v3` | `56afc609e74202658d3ffba0e8f6dda462b719fa` |
| `actions/deploy-pages` | `v4` | `d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e` |

Reviewed on **2026-11-07** against each upstream `refs/tags/<version>` using the GitHub REST API. This document intentionally does **not** claim these versions are the latest forever.

## Maintenance contract

1. Keep the existing architecture and OS-specific product CI intact. A first-party Action upgrade is infrastructure-only and must **not** change `.github/release-paths.txt` or ship a GitHub Release by itself.
2. Update Actions together where practicable, using one reviewable PR per repository. Before merging, verify actual PR CI, including ZIP and SHA-256 contracts; then check `main` runs and skipped publishing steps.
3. Only project release jobs need `contents: write`. Leave normal CI `contents: read`; set `persist-credentials: false` in checkout steps unless a specific authorized write requires otherwise.
4. Do not automatically deploy the Filamentra-DataSource GitHub Pages demo as part of a pin update. Its workflow is intentionally manual.
5. Shared 4FusionLab composite Actions are separate: consumers pin `4FusionLab/.github/.github/actions/*` to the reviewed platform commit SHA. GitVersion.Tool remains `6.8.2`.
6. When changing a pin, resolve the tag through upstream GitHub, read breaking changes, update this table and the consumer PRs, and keep version comments next to pinned `uses:` lines.
