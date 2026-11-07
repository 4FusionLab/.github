# Product README guidelines

[Русская версия](README_GUIDELINES.ru.md)

Use these rules when creating, reviewing, or changing a 4FusionLab product's main pages. Adapt the length and sections to the product; a planned product must not look like a released one.

## Structure

1. Start with the product name, Autodesk Fusion, and one sentence explaining the user's outcome. Add existing product artwork with useful alt text when available; do not invent screenshots.
2. Put links to the other language, downloads when an installable release exists, and support near the top. Link to the actual release or releases page, not a promised download.
3. Explain the current workflow and capabilities, then provide installation steps and the command location. For unreleased work, state its status and omit fictional installation steps.
4. State material limitations, data or save risks, supported geometry and platform status near the relevant claims. Separate manifest support, automated tests and actual native Fusion acceptance. Put critical warnings before the workflow and download instructions.
5. Link existing guides, release notes, development, support and license material as appropriate. Preserve useful examples, screenshots, credits and product-specific detail. Use relative links for files in the repository.

## Language and accuracy

- Write documents in English. Maintain a separate Russian version of documentation, with equivalent meaning, warnings, links and examples; intermediate working notes do not require translation. Use `README.md` and `README.ru.md` as the main pair, and link them in both directions. Keep any existing legacy path usable and synchronized or redirect it to the canonical version.
- Keep actual Fusion command and control names in English in both versions. Translate prose and image alt text for the audience. Do not copy an English product description into Russian as a substitute for a translation.
- Verify claims against the relevant code, manifest, release assets and test evidence. Distinguish current behavior from plans and experiments. Avoid precise version numbers or badges that will become stale unless they serve a clear purpose and have an owner.
- Before changing a license statement or badge, inspect the current `LICENSE` and applicable distribution terms, including concurrent work. Link to those terms; do not infer commercial permissions from another product. Never change a license as part of a style edit.

## Review before delivery

Check the two language versions section by section for equivalent claims and warnings; check relative file, image and anchor links and the release URL; check that installation names match the shipped archive. Review the diff for removed material and license conflicts. Run the repository's relevant documentation and project checks, and report what was actually verified. A documentation-only change is not native Fusion validation and must follow the shared release policy.
