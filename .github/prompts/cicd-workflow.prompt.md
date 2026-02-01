---
agent: agent
description: Create or modify GitHub Actions workflows for CI/CD
---

# CI/CD Workflow

## Context

I need to create or modify a GitHub Actions workflow for Azure governance (policies, initiatives, assignments).

## Discovery

Analyze existing workflows with `#codebase` in `.github/workflows/`.

## Input Required

- **Workflow name**: ${input:workflow_name}
- **Purpose**: ${input:purpose}

## Template

```yaml
# 📋 {workflow_name}.yml
# 🎯 Purpose: {purpose}

name: {workflow_name}

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  id-token: write
  contents: read

env:
  ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
  ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}
  ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}
  ARM_USE_OIDC: true

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - name: 📥 Checkout
        uses: actions/checkout@v4

      - name: 🔐 Azure Login
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.ARM_CLIENT_ID }}
          tenant-id: ${{ secrets.ARM_TENANT_ID }}
          subscription-id: ${{ secrets.ARM_SUBSCRIPTION_ID }}

      - name: 🏗️ Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "~> 1.7"
```

## References

Follow conventions in `#file:.github/copilot-instructions.md`
