---
applyTo: "**/*.py"
---

# Python Instructions

## Mandatory rules
- Start scripts with a module docstring containing purpose and usage examples.
- Use emoji logs for key execution states.
- Prefer early return and clear guard clauses.
- Keep code explicit and readable.
- Unit tests are required for testable logic.
- Apply these rules for both create and modify operations.

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
