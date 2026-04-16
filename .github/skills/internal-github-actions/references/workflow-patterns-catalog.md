# Workflow Patterns Catalog

Use this catalog when the baseline example is too small but a repository-specific one-off workflow would still repeat known shapes.

## Matrix validation

```yaml
strategy:
  fail-fast: false
  matrix:
    os: [ubuntu-latest, macos-latest]
    runtime: ['18', '20']
```

- Use when the same checks must run across versions or platforms.
- Keep the steps identical across matrix entries and vary only the inputs.
- Add `max-parallel` when runners or external quotas are limited.

## Reusable workflow delegation

```yaml
jobs:
  validate:
    uses: ./.github/workflows/reusable-validate.yml
    with:
      working-directory: services/api
```

- Use when the reusable unit is one or more jobs.
- Keep caller inputs small and typed.
- Expose only the outputs that downstream jobs actually need.

## Environment-gated manual deploy

```yaml
concurrency:
  group: deploy-${{ github.ref }}-${{ inputs.target }}
  cancel-in-progress: false

environment:
  name: production
```

- Validate the target in an earlier job and deploy only from the normalized value.
- Keep deployment permissions and secrets scoped to the deploy job.
- Use protected environments instead of bespoke approval logic in shell steps.

## Scheduled housekeeping

```yaml
on:
  schedule:
    - cron: '17 3 * * 1'
```

- Make scheduled jobs idempotent and safe to rerun.
- Add explicit `timeout-minutes` and narrow `permissions`.
- Avoid destructive mutations unless the workflow revalidates state and emits clear logs or notifications.
