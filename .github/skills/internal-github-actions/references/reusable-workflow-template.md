# Reusable Workflow Template

Use this starter when multiple workflows in one repository need the same job orchestration through `workflow_call`.

```yaml
name: reusable-validate

on:
  workflow_call:
    inputs:
      working-directory:
        description: Directory to validate
        required: false
        type: string
        default: .
    outputs:
      normalized-working-directory:
        description: Sanitized directory forwarded to caller jobs
        value: ${{ jobs.validate.outputs.working-directory }}

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    outputs:
      working-directory: ${{ steps.normalize.outputs.working-directory }}
    steps:
      - name: Check out repository
        # actions/checkout@v6.0.2
        # https://github.com/actions/checkout/releases/tag/v6.0.2
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd
      - name: Normalize caller input
        id: normalize
        env:
          WORKING_DIRECTORY: ${{ inputs.working-directory }}
        run: |
          set -euo pipefail
          if [[ ! -d "$WORKING_DIRECTORY" ]]; then
            echo "working-directory does not exist: $WORKING_DIRECTORY" >&2
            exit 1
          fi
          echo "working-directory=$WORKING_DIRECTORY" >> "$GITHUB_OUTPUT"
      - name: Run validation
        working-directory: ${{ steps.normalize.outputs.working-directory }}
        run: make test
```

Use a reusable workflow when:

- the unit of reuse is one or more jobs rather than a step sequence
- the callee needs its own `permissions`, `runs-on`, or `concurrency`
- the caller should pass typed inputs or consume workflow outputs

Prefer a composite action instead when the reusable unit is step-level logic inside a job.
