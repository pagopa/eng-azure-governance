---
description: Add or improve unit tests for Python, Java, or Node.js code
name: cs-add-unit-tests
agent: agent
argument-hint: language=<python|java|nodejs> target_file=<path> [test_framework=<name>]
---

# Add Unit Tests

## Context
Add or improve unit tests for an existing script or module while preserving repository conventions.

## Required inputs
- **Language**: ${input:language:python,java,nodejs}
- **Target file**: ${input:target_file}
- **Test framework**: ${input:test_framework:python=repo-default|java=junit5|nodejs=node:test}

## Instructions

1. Use the matching skill:
   - Python: `.github/skills/script-python/SKILL.md`
   - Java: `.github/skills/project-java/SKILL.md`
   - Node.js: `.github/skills/project-nodejs/SKILL.md`
2. Inspect `${input:target_file}` and identify testable behavior.
3. Add or update tests covering:
   - happy path
   - input validation and guard clauses
   - relevant edge cases
4. Keep tests deterministic and isolated (no network calls in unit scope).
5. Use a simple default stack:
   - Java: JUnit 5
   - Node.js: `node:test` + `node:assert/strict`
6. Prefer readability and simple assertions over complex test abstractions.
7. Use BDD-like naming (`given_when_then` or clear `describe`/`it` grouping).
8. If language is Python and external dependencies are needed for the script, ensure `requirements.txt` uses pinned versions.
9. Do not create unit tests for Bash unless explicitly requested.

## Minimal example
- Input: `language=python target_file=src/scripts/report.py`
- Expected output:
  - Tests under `tests/` covering success, validation, and edge behavior.
  - Deterministic assertions and no network calls.
  - Updated dependency pinning only if new external libs are introduced.

## Validation
- Run the project's unit test command for the selected language/framework.
- Report which test cases were added and why.
