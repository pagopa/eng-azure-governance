---
description: YAML formatting and clarity conventions for stable, maintainable configuration files.
applyTo: "**/*.yml,**/*.yaml"
---

# YAML Instructions

## Formatting

- Use 2-space indentation.
- Avoid tabs.
- Keep key names stable and readable.

## Best practices

- Quote values only when needed for correctness.
- Keep anchors/aliases simple; prefer clarity.
- Keep comments concise and in English.

## Validation

- Validate syntax before commit.
- Reuse existing schema/style in the target repository.
- For GitHub Actions workflows, validate against the GitHub Actions schema when available.
