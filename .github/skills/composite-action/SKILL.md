---
name: composite-action
description: Create or modify reusable GitHub composite actions with secure Bash and deterministic behavior.
---

# Composite Action Skill

## When to use
- Create a new reusable composite action under `.github/actions/`.
- Modify an existing composite action and preserve compatibility.
- Standardize input validation and shell execution patterns.

## Mandatory rules
- Keep the action focused on one responsibility.
- Define explicit `name`, `description`, and typed `inputs`.
- Validate required inputs early and fail fast.
- Use English logs and deterministic output.
- Prefer shell scripts for complex logic instead of large inline blocks.

## Security rules
- Quote shell variables.
- Avoid `eval` and untrusted command execution.
- Pass expression inputs via `env` for shell consumption.
- Keep secrets out of defaults and logs.

## Minimal template
```yaml
name: Validate Input
description: Validate required inputs before action logic
inputs:
  target:
    description: Target environment
    required: true
runs:
  using: composite
  steps:
    - shell: bash
      env:
        TARGET: ${{ inputs.target }}
      run: |
        set -euo pipefail
        if [[ -z "$TARGET" ]]; then
          echo "❌ target is required" >&2
          exit 1
        fi
        echo "✅ input validated"
```

## Checklist
- [ ] Inputs documented and validated.
- [ ] Shell code is safe (`set -euo pipefail`, quoted vars).
- [ ] No secret leakage in logs/defaults.
- [ ] Backward compatibility preserved when modifying existing action.
