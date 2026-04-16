---
description: Composite-action-specific standards that extend the GitHub Actions baseline with input validation and safe shell patterns.
applyTo: "**/actions/**/action.y*ml"
---

# Composite Action Instructions

## Scope
- This instruction augments `.github/instructions/internal-github-actions.instructions.md`.
- Keep only composite-specific rules here.

## Composite-specific rules
- Define explicit `inputs` and `outputs`, and keep published names stable for existing callers.
- Validate required values early and fail before the main logic runs.
- Pass `${{ inputs.* }}` through `env:` before shell usage.
- Use `$GITHUB_OUTPUT` and `$GITHUB_ENV` for multi-step coordination instead of ad hoc temp files when shell steps need to share state.
- Keep `shell: bash` explicit and start shell blocks with `set -euo pipefail`.
- Move longer logic into dedicated scripts instead of large inline `run:` blocks.
- Document inputs, outputs, and a minimal usage example next to the action.
- Keep a lightweight happy-path validation path before release, such as a smoke workflow or fixture-based script.
- Preserve backward-compatible input and output contracts when modifying an existing composite action.
