---
description: Security and reliability standards for GitHub Actions workflows with SHA pinning and least privilege.
applyTo: "**/workflows/**"
---

# GitHub Actions Instructions

## Security baseline
- Prefer OIDC over long-lived secrets.
- Pin actions to full-length commit SHAs.
- For each pinned SHA, add an adjacent comment with release/tag and upstream release URL.
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
steps:
  - name: Checkout
    uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608 # v4.1.7 https://github.com/actions/checkout/releases/tag/v4.1.7

concurrency:
  group: example-${{ github.ref }}
  cancel-in-progress: true

permissions:
  id-token: write
  contents: read
```
