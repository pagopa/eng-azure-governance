---
description: Create or modify a reusable GitHub composite action
name: cs-composite-action
agent: agent
argument-hint: action=<create|modify> action_name=<name> purpose=<purpose> [action_path=.github/actions/<name>/action.yml]
---

# Composite Action Task

## Required inputs
- **Action**: ${input:action:create,modify}
- **Action name**: ${input:action_name}
- **Purpose**: ${input:purpose}
- **Action path**: ${input:action_path:.github/actions/action-name/action.yml}

## Instructions
1. Use `.github/skills/composite-action/SKILL.md`.
2. Apply `.github/instructions/github-action-composite.instructions.md`.
3. If `action=modify`, preserve public inputs/outputs unless changes are explicitly requested.
4. Keep logs, comments, and user-facing output in English.
5. Keep shell logic readable; move complex logic to scripts when needed.

## Minimal example
- Input: `action=create action_name=validate-input purpose="Validate required inputs for deployment"`
- Expected output:
  - A composite action file with explicit inputs and safe shell execution.
  - Early validation with clear failure messages.
  - No secret leakage and deterministic logs.

## Validation
- Validate YAML syntax.
- Validate input handling and failure paths.
- Verify no unsafe shell patterns (`eval`, unquoted variable expansion).
