# Output Forwarding Pattern

Use this pattern when a composite action computes a value in one step and needs to expose it to callers as an action output.

```yaml
name: Normalize Target
description: Validate and forward a deployment target
inputs:
  target:
    description: Deployment target
    required: true
outputs:
  normalized-target:
    description: Lowercase target value for caller workflows
    value: ${{ steps.normalize.outputs.normalized-target }}
runs:
  using: composite
  steps:
    - name: Validate input
      shell: bash
      env:
        TARGET: ${{ inputs.target }}
      run: |
        set -euo pipefail
        if [[ -z "$TARGET" ]]; then
          echo "target is required" >&2
          exit 1
        fi
    - name: Normalize target
      id: normalize
      shell: bash
      env:
        TARGET: ${{ inputs.target }}
      run: |
        set -euo pipefail
        value="$(printf '%s' "$TARGET" | tr '[:upper:]' '[:lower:]')"
        echo "normalized-target=$value" >> "$GITHUB_OUTPUT"
        echo "NORMALIZED_TARGET=$value" >> "$GITHUB_ENV"
```

Keep the contract stable:

- declare the public output in `outputs:`
- give the producing step an `id`
- write caller-visible key-value pairs to `$GITHUB_OUTPUT`
- use `$GITHUB_ENV` only for step-to-step state inside the action

Do not forward values through temp files when `$GITHUB_OUTPUT` and `$GITHUB_ENV` already express the contract clearly.
