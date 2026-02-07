---
applyTo: ".github/workflows/**"
---

# GitHub Actions Instructions

## Security baseline
- Prefer OIDC over long-lived secrets.
- Pin actions to full-length commit SHAs.
- Keep `permissions` minimal.
- Avoid `pull_request_target` for untrusted code.

## Workflow baseline
- Set explicit `timeout-minutes`.
- Set `concurrency` when jobs can conflict on shared targets.
- Prefer reusable workflows (`workflow_call`) for repeated pipelines.
- Use clear English step names.
- For Terraform jobs: include `fmt -check`, use `-input=false`, and avoid concurrent apply on the same target.
- Keep environment secrets in protected environments when possible.
- Keep cache and artifact usage explicit and deterministic.
- Use matrix strategy only when it improves confidence/cost tradeoff.

## Minimal example
```yaml
concurrency:
  group: example-${{ github.ref }}
  cancel-in-progress: true

permissions:
  id-token: write
  contents: read
```
