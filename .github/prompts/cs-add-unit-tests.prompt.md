---
description: Add or improve unit tests for Python code
name: cs-add-unit-tests
agent: agent
argument-hint: target_file=<path> [test_framework=<name>]
---

# Add Unit Tests

## Context
Add or improve unit tests for an existing Python module or script while preserving repository conventions.

## Required inputs
- **Target file**: ${input:target_file}
- **Test framework**: ${input:test_framework:pytest}

## Instructions

1. Use the skill in `.github/skills/script-python/SKILL.md`.
2. Inspect `${input:target_file}` and identify testable behavior.
3. Add or update tests covering:
   - happy path
   - input validation and guard clauses
   - relevant edge cases
4. Keep tests deterministic and isolated (no network calls in unit scope).
5. Prefer readability and simple assertions over complex test abstractions.
6. Use clear naming for test cases.
7. If external dependencies are needed for tests, ensure pinned versions where repository conventions require it.

## Minimal example
- Input: `target_file=src/scripts/report.py`
- Expected output:
  - Tests under `tests/` covering success, validation, and edge behavior.
  - Deterministic assertions and no network calls.

## Validation
- Run `python -m pytest` (or repository equivalent).
- Report which test cases were added and why.
