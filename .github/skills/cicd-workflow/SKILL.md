---
name: cicd-workflow
description: Create or modify secure GitHub Actions workflows for CI/CD pipelines.
---

# CI/CD Workflow Skill

## When to use
- Create or modify workflows.
- Add CI/CD jobs.
- Add cloud auth for Terraform or deployment steps.

## Mandatory rules
- Prefer OIDC.
- Pin every action to a full-length SHA.
- Keep `permissions` least-privilege.
- Keep step names and operational output in English.

## Minimal workflow example
```yaml
name: CI
on: [pull_request]

permissions:
  contents: read
  id-token: write

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<FULL_LENGTH_COMMIT_SHA>
      - run: terraform fmt -check -recursive
```

## Auth snippets

### AWS
```yaml
- uses: aws-actions/configure-aws-credentials@<FULL_LENGTH_COMMIT_SHA>
```

### Azure
```yaml
- uses: azure/login@<FULL_LENGTH_COMMIT_SHA>
```

### GCP
```yaml
- uses: google-github-actions/auth@<FULL_LENGTH_COMMIT_SHA>
```

## Checklist
- [ ] OIDC configured.
- [ ] Actions pinned by SHA.
- [ ] `permissions` minimized.
- [ ] Environment protection enabled for production.
- [ ] Validation steps included (for example, `terraform fmt -check`).
