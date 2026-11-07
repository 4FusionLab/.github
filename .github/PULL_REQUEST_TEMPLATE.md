## Summary

Describe the user-facing value and why this change is needed.

## Scope and verification

- [ ] Project-specific `AGENTS.md` and relevant docs were checked
- [ ] Relevant unit/integration tests passed (include commands and results)
- [ ] Impact on native Fusion behaviour and OS compatibility is described
- [ ] Existing Fusion manifest IDs and backward compatibility are preserved
- [ ] No credentials, generated build files or user CAD data added

## Release impact

- [ ] Runtime/packaging inputs changed → an automatic release is expected after CI passes on `main`
- [ ] Documentation/tests/CI only → no GitHub Release should be created
- [ ] `.github/release-paths.txt` was updated if shipped-runtime scope changed

## User documentation

- [ ] Existing EN and RU guides were updated where relevant, or not applicable

> Never manually create a tag or GitHub Release for a normal `main` push/merge. This template is a checklist, not an instruction to bypass existing review, platform validation or native-CAD acceptance.
