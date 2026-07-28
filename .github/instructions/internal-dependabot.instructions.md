---
description: Dependabot review checks for safe update scope, manageable PR volume, and security coverage.
applyTo: "**/.github/dependabot.yml,**/.github/dependabot.yaml"
excludeAgent: "cloud-agent"
---

# Dependabot Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Flag missing package ecosystems or directories that leave active manifests uncovered.
- Flag schedules that are too aggressive or too sparse for the repository risk profile.
- Flag missing grouping strategy where update volume can create avoidable PR noise.
- Flag ignore rules that suppress security-relevant updates without clear scope.
- Flag missing or incorrect target-branch settings for intended update flow.
- Flag update configuration that expands permissions or scope beyond least-privilege intent.
