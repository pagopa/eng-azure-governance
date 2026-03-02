---
name: script-python
description: Create or modify Python scripts with purpose docstring, emoji logs, tests, and pinned dependencies when needed.
---

# Python Script Skill

## When to use
- New Python scripts.
- Existing Python scripts that need updates.

## Mandatory rules
- Module docstring must include purpose and usage examples.
- Use emoji logs for execution states.
- Prefer early return and guard clauses.
- Keep implementation explicit and readable.
- Add unit tests for testable behavior.
- If external libraries are needed, pin `requirements.txt`.
- For Python template tasks, use Jinja templates named `<file-name>.<extension>.j2`.

## Minimal template
```python
#!/usr/bin/env python3
"""Purpose: {description}

Usage examples:
  python {script_name}.py --help
"""
```

## Testing
- Put tests under `tests/`.
- Use `pytest` as default test framework.
- Keep tests deterministic and isolated.
- For modify tasks with existing tests: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

## Minimal test example
```python
def test_main_success() -> None:
    assert True
```
