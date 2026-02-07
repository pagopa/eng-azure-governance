---
applyTo: ".github/actions/**/action.y*ml"
---

# Composite Action Instructions

## Objective
Define consistent standards for reusable composite actions under `.github/actions/`.

## Mandatory rules
- Keep each composite action focused on one clear responsibility.
- Use explicit `name`, `description`, and typed `inputs`.
- Validate required inputs early and fail fast with clear errors.
- Use English logs and keep output deterministic.
- Avoid embedding secrets in scripts or defaults.
- Prefer shell scripts in `.github/scripts/` for complex logic.

## Security baseline
- Quote all interpolated shell variables.
- Avoid `eval` and untrusted command execution.
- Minimize permissions in calling workflows.
- Document expected trust model in the action description.

## Minimal example
```yaml
name: "Validate Input"
description: "Validate required inputs before running workflow logic"
inputs:
  target:
    description: "Target environment"
    required: true
runs:
  using: "composite"
  steps:
    - shell: bash
      run: |
        set -euo pipefail
        if [[ -z "${{ inputs.target }}" ]]; then
          echo "❌ target is required" >&2
          exit 1
        fi
        echo "✅ target input validated"
```
