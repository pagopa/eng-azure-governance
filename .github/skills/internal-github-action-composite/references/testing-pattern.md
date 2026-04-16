# Composite Action Testing Pattern

Use a small layered strategy instead of assuming the action works because `action.yml` looks correct.

## 1. Smoke workflow

Run the action from a workflow that checks out the repository, calls the local action, and asserts one success-path output.

```yaml
jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        # actions/checkout@v6.0.2
        # https://github.com/actions/checkout/releases/tag/v6.0.2
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd
      - name: Run local action
        id: action
        uses: ./.github/actions/package-directory
        with:
          source-directory: tests/fixtures/package-directory
      - name: Assert archive output
        shell: bash
        env:
          ARCHIVE_PATH: ${{ steps.action.outputs.archive-path }}
        run: |
          set -euo pipefail
          test -n "$ARCHIVE_PATH"
          test -f "$ARCHIVE_PATH"
```

## 2. Failure-path check

- Trigger at least one invalid input case and assert the action fails early with a clear error.

## 3. Contract check

- Keep README inputs and outputs in sync with `action.yml`.
- Re-run smoke checks when adding or renaming any input or output.
- Treat output name changes as compatibility changes, not as harmless refactors.
