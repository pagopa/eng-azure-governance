# Workflow Archetype: Validated Manual Deploy

Use this starter when a workflow needs a manual entrypoint, input validation, and protected deployment gates without turning into a one-size-fits-all catalog.

```yaml
name: deploy-service

on:
  workflow_dispatch:
    inputs:
      target:
        description: Deployment target
        required: true
        type: choice
        options:
          - staging
          - production

permissions:
  contents: read
  deployments: write

concurrency:
  group: deploy-${{ github.ref }}-${{ inputs.target }}
  cancel-in-progress: false

jobs:
  validate:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    outputs:
      target: ${{ steps.target.outputs.value }}
    steps:
      - name: Check out repository
        # actions/checkout@v6.0.2
        # https://github.com/actions/checkout/releases/tag/v6.0.2
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd
      - name: Validate dispatch input
        id: target
        env:
          TARGET: ${{ inputs.target }}
        run: |
          set -euo pipefail
          case "$TARGET" in
            staging|production) ;;
            *)
              echo "Unsupported target: $TARGET" >&2
              exit 1
              ;;
          esac
          echo "value=$TARGET" >> "$GITHUB_OUTPUT"
      - name: Run pre-deploy checks
        run: make test

  deploy:
    needs: validate
    if: ${{ needs.validate.outputs.target != '' }}
    runs-on: ubuntu-latest
    timeout-minutes: 20
    environment:
      name: ${{ needs.validate.outputs.target }}
    steps:
      - name: Check out repository
        # actions/checkout@v6.0.2
        # https://github.com/actions/checkout/releases/tag/v6.0.2
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd
      - name: Deploy
        env:
          TARGET: ${{ needs.validate.outputs.target }}
        run: |
          set -euo pipefail
          ./scripts/deploy.sh "$TARGET"
```

Adapt this archetype by:

- adding `workflow_call` when the same deploy orchestration is reused inside the repository
- introducing artifacts with explicit `retention-days` only when a reviewed handoff is required
- moving repeated step logic into a composite action instead of expanding the deploy job inline
