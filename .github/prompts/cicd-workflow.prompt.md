---
agent: agent
description: Create or modify GitHub Actions workflows for CI/CD
---

# CI/CD Workflow

## Context

I need to create or modify a GitHub Actions workflow for Azure governance (policies, initiatives, assignments).

## Inputs

- **Workflow name**: ${input:workflow_name}
- **Purpose**: ${input:purpose}

## Steps

1. Use the `cicd-workflow` skill in `.github/skills/cicd-workflow/SKILL.md`.
2. Analyze existing workflows with `#codebase` in `.github/workflows/`.
3. Implement changes following the skill template and repository instructions.

## Validations

- Validate the workflow YAML (check `#problems`).
