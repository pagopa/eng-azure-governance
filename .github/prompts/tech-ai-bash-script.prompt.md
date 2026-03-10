---
description: Create or modify repository-agnostic Bash scripts with strict mode and readable flow
name: TechAIBashScript
agent: agent
argument-hint: action=<create|modify> script_name=<name> purpose=<purpose> [target_path=<path>] [target_file=<path>]
---

# TechAI Bash Script

## Context
Create or modify a Bash script while keeping behavior explicit, reusable, and easy to validate.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}
- **Target path**: ${input:target_path:.github/scripts}
- **Target file (when modifying)**: ${input:target_file}

## Instructions
1. Use `.github/skills/tech-ai-script-bash/SKILL.md`.
2. Reuse existing repository patterns before introducing new structure.
3. Keep `#!/usr/bin/env bash`, `set -euo pipefail`, a short purpose/usage header, English logs, and guard clauses.
4. Preserve existing behavior on modify tasks unless a change is explicitly requested.
5. Avoid repository-specific assumptions in paths, credentials, and business semantics unless the task requires them.
6. Make new scripts executable.

## Minimal example
- Input: `action=create script_name=check-frontmatter purpose="Validate markdown frontmatter" target_path=.github/scripts`
- Expected output:
  - Reusable Bash script with strict mode, English logs, and guard clauses.

## Validation
- Run `bash -n` on the changed script.
- Run `shellcheck -s bash` when available.
- Run `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict` when changing Copilot assets.
