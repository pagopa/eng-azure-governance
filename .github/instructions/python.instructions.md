---
description: Python standards for both scripts and application code with DDD boundaries, guard clauses, and pytest defaults.
applyTo: "**/*.py"
---

# Python Instructions

## Mandatory rules
- Use emoji logs for key execution states.
- Prefer early return and clear guard clauses.
- Keep code explicit and readable.
- Unit tests are required for testable logic.
- Apply these rules for both create and modify operations.
- For Python template tasks, use Jinja templates named `<file-name>.<extension>.j2`.
- Keep template content complete and externalize only values intentionally passed by the caller.

## Application code (non-script)
- Apply DDD boundaries for non-trivial features: domain, application, and infrastructure concerns must stay separated.
- Keep business rules in domain entities/value objects/domain services.
- Keep infrastructure concerns (DB, API clients, cloud SDK) in adapters and repositories.
- Use ubiquitous language in domain classes, method names, and errors.

## Script code
- Start scripts with a module docstring containing purpose and usage examples.
- Keep CLI parsing and orchestration explicit.
- Avoid embedding domain rules that belong to reusable application modules.

## Style
- Follow PEP8.
- Use type hints in function signatures.
- Keep line length <= 120.

## Output language
- Docstrings, logs, exceptions, and CLI output must be in English.

## Dependencies
- If external libraries are needed, pin versions in `requirements.txt`.

## Testing defaults
- Use `pytest` as default unit-test framework.
- Keep tests under `tests/` with deterministic behavior.
- For modify tasks with existing tests: edit code first, run existing tests, then update tests only if behavior changes are intentional.

## Minimal skeleton
```python
#!/usr/bin/env python3
"""Purpose: Explain what this script does.

Usage examples:
  python script.py --help
"""
```

## Minimal test example
```python
def test_example() -> None:
    assert 1 + 1 == 2
```
