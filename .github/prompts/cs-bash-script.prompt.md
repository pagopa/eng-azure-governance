---
description: Create or modify a Bash script with standard structure
name: cs-bash-script
agent: agent
argument-hint: action=<create|modify> script_name=<name> purpose=<purpose> [location=scripts] [target_file=<path>]
---

# Bash Script Task

## Context
Create or modify a Bash script following repository standards.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}
- **Location**: ${input:location:scripts}
- **Target file (when modifying)**: ${input:target_file}

## Instructions

1. Use the skill in `.github/skills/script-bash/SKILL.md`.
2. Search for existing scripts in the repository to reuse patterns.
3. Create or update the script with:
   - `#!/usr/bin/env bash`
   - initial comment block with purpose and usage examples
   - `set -euo pipefail`
   - emoji logging functions
   - early return guard clauses
   - readable and simple control flow
4. If `action=modify`, preserve existing behavior unless explicit changes are requested.
5. Do not add unit tests for Bash unless explicitly requested.
6. Make the file executable.

## Minimal example
- Input: `action=create script_name=sync-users purpose="Sync users from CSV"`
- Expected output:
  - Executable Bash script with purpose/usage header.
  - Guard clauses, emoji log helpers, and readable flow.
  - No behavior beyond requested scope.

## Validation
- Run `bash -n` on the script.
- Run `shellcheck -s bash` when available.
