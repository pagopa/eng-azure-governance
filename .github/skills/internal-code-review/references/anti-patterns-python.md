# Python Anti-Patterns

Reference: `instructions/internal-python.instructions.md`

## Critical

| ID | Anti-pattern | Why |
|---|---|---|
| PY-C01 | Hardcoded secrets, tokens, or passwords | Credential exposure risk |
| PY-C02 | `eval()` or `exec()` on untrusted input | Arbitrary code execution |
| PY-C03 | `pickle.load()` / `pickle.loads()` on untrusted data | Deserialization attack |

## Major

| ID | Anti-pattern | Why |
|---|---|---|
| PY-M01 | Bare `except:` or `except Exception:` without re-raise or logging | Swallows errors silently |
| PY-M02 | Mutable default arguments (`def f(items=[])`) | Shared state across calls |
| PY-M03 | `os.system()` or `subprocess` with `shell=True` | Shell injection risk |
| PY-M04 | Missing type hints on public function signatures | Reduces readability and tooling support |
| PY-M05 | Function body longer than 40 lines (excluding docstring) | Complexity and testability concern |
| PY-M06 | Cyclomatic complexity > 10 per function | Hard to test and maintain |
| PY-M07 | `print()` instead of `logging` in application/library code | No log level control in production |
| PY-M08 | Missing unit tests for new public functions | Violates test coverage mandate |
| PY-M09 | Python tests outside repository-root `tests/` or without mirrored source paths | Breaks repository test discoverability and ownership mapping |

## Minor

| ID | Anti-pattern | Why |
|---|---|---|
| PY-m01 | Unused imports | Dead code noise |
| PY-m02 | Hardcoded file paths or URLs | Portability and configuration concern |
| PY-m03 | Missing docstring on public functions/classes | Reduces discoverability |
| PY-m04 | `noqa` or `type: ignore` without inline justification | Hides real issues |
| PY-m05 | Mixed `str.format()` and f-strings in the same module | Style inconsistency |
| PY-m06 | Dead code (unreachable branches, commented-out blocks) | Maintenance burden |
| PY-m07 | Missing `__all__` in modules with public API | Ambiguous public surface |
| PY-m08 | Nested functions deeper than 2 levels | Readability concern |

## Nit

| ID | Anti-pattern | Why |
|---|---|---|
| PY-N01 | Line length > 120 characters | PEP8 / repo convention |
| PY-N02 | Missing trailing newline at end of file | POSIX convention |
| PY-N03 | Inconsistent quote style (single vs double) within a module | Style preference |
| PY-N04 | Import not sorted (stdlib → third-party → local) | Convention consistency |
| PY-N05 | Variable named `l`, `O`, `I` (ambiguous with digits) | Readability |
| PY-N06 | Missing empty line between logical sections | Visual structure |

## Good vs bad examples

```python
# BAD (PY-M01): bare except
try:
    result = fetch_data()
except:
    pass

# GOOD: specific exception, logged
try:
    result = fetch_data()
except requests.RequestException as exc:
    logger.warning("⚠️ Fetch failed: %s", exc)
    raise
```

```python
# BAD (PY-M02): mutable default
def add_item(name: str, items: list = []) -> list:
    items.append(name)
    return items

# GOOD: None sentinel
def add_item(name: str, items: list | None = None) -> list:
    if items is None:
        items = []
    items.append(name)
    return items
```

```python
# BAD (PY-M07): print in library code
def process(data):
    print(f"Processing {len(data)} items")

# GOOD: structured logging
import logging
logger = logging.getLogger(__name__)

def process(data: list[dict]) -> None:
    logger.info("ℹ️ Processing %d items", len(data))
```
