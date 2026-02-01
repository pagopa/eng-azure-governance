---
agent: agent
description: Create Python scripts with test suite for complex operations
---

# Create Python Script

## Context

I need to create a Python script for complex operations in Azure governance (policies, remediation).

## Inputs

- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}

## Steps

1. Use the `script-python` skill in `.github/skills/script-python/SKILL.md`.
2. Use `#codebase` to search for existing Python scripts in `src/scripts/`.
3. Implement changes following the skill template and repository instructions.

## Validations

- Check `#problems` for errors after changes.
