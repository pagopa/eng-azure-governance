---
name: project-python
description: Create or modify Python application components using DDD boundaries, early returns, and deterministic pytest coverage.
---

# Python Project Skill

## When to use
- Services, use cases, adapters, repositories, and domain modules in Python applications.
- Refactoring or extending existing Python application components.
- Non-script Python code that contains domain behavior.

## Mandatory rules
- Apply DDD boundaries: domain, application, and infrastructure concerns must be separated.
- Keep business rules in domain entities/value objects/domain services.
- Keep I/O and SDK clients in infrastructure adapters.
- Use ubiquitous language in domain classes, methods, and exceptions.
- Prefer early return and guard clauses.
- Keep code explicit and readability-first.
- Add unit tests for testable logic.

## Testing
- Use `pytest`.
- Keep tests deterministic and isolated.
- Prefer BDD-like names in the `given_when_then` style.
- For modify tasks with existing tests: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

## Minimal module example
```python
"""Purpose: Resolve account status based on domain rules."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AccountId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("account id is required")


def resolve_account_state(account_id: AccountId, is_locked: bool) -> str:
    if is_locked:
        return "locked"
    return f"active:{account_id.value}"
```

## Minimal test example
```python
import pytest


def test_given_blank_account_id_when_creating_then_raises_value_error() -> None:
    with pytest.raises(ValueError):
        AccountId(" ")
```
