---
description: Create or modify a Python script with standard structure
name: cs-python-script
agent: agent
argument-hint: action=<create|modify> script_name=<name> purpose=<purpose> [location=src/scripts] [target_file=<path>]
---

# Python Script Task

## Context
Create or modify a Python script following repository standards.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}
- **Location**: ${input:location:src/scripts}
- **Target file (when modifying)**: ${input:target_file}

## Instructions

1. Use the skill in `.github/skills/script-python/SKILL.md`.
2. Search for existing scripts in the repository to reuse patterns.
3. Create or update the script with:
   - module docstring containing purpose and usage examples
   - argparse for CLI arguments
   - emoji logging
   - early return guard clauses
   - readable and explicit control flow
4. If `action=modify`, preserve existing behavior unless explicit changes are requested.
5. If the task includes template files, use Jinja templates named `<file-name>.<extension>.j2`.
6. If `action=modify` and tests already exist, run existing tests before editing test files.
7. Create or update tests in `tests/test_{script_name}.py` only after the first test run, and only for intentional behavior changes or uncovered new behavior.
8. If external libraries are required, create/update `requirements.txt` with pinned versions.

## Minimal example
- Input: `action=modify script_name=report purpose="Generate monthly report" target_file=src/scripts/report.py`
- Expected output:
  - Updated script with purpose/usage docstring and early-return flow.
  - Added/updated deterministic unit tests under `tests/`.
  - Pinned dependency updates only if external libs changed.

## Validation
- Check syntax errors.
- Verify import availability.
- Run unit tests.
