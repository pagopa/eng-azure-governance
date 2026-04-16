---
name: internal-project-python
description: Use when creating or modifying Python package or application code whose primary contract is imported behavior, service boundaries, or framework-owned flows rather than operator-facing scripts.
---

# Python Project Skill

Follow `.github/instructions/internal-python.instructions.md` for the baseline Python rules. This skill adds application-specific guidance only.

## When to use
- Services, use cases, adapters, packages, and modules in Python applications.
- Refactoring or extending existing Python application components.
- Reusable Python code whose primary contract is imported behavior rather than operator-facing execution.

## Boundary
- This skill covers structured package, library, or application components whose primary contract is reusable domain, service, or framework behavior.
- Small operator-facing tools remain out of scope even when they have multiple files or tests.
- A `lib/` folder, root-level tests, or multiple entrypoints alone do not make a tool application code.

## Application-specific guidance
- Use type hints on public APIs and keep data contracts explicit.
- Choose async only when the workload is I/O-bound and the surrounding stack supports it cleanly.
- Keep request or transport models, domain logic, and persistence concerns in separate modules.

Load `references/examples.md` when you need a minimal module or test example.

## Testing
- Follow the repository pytest defaults from the instruction owner.
- BDD-like names: `given_when_then` style.
- Prefer fixtures, parameterization, and mocking only when they reduce duplication or isolate real external boundaries.
- Use coverage reports to close meaningful behavioral gaps, not as a blanket 100% doctrine.
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

## Architecture and framework guidance
- Follow the repository's existing framework before introducing FastAPI, Flask, Django, or a new dependency stack.
- Use dataclasses or typed DTOs for internal contracts, and boundary-validation models where the framework already expects them.
- Keep async flows end-to-end; do not mix blocking libraries into async request paths without an explicit bridge.

## Test-shape guidance
- Use parameterized tests for behavior that varies across a small, explicit input matrix.
- Mock network, filesystem, database, or queue boundaries; do not mock internal business logic seams by default.
- Use property-based testing only when the input space is large enough to justify it.
- Prefer targeted coverage growth on changed code and risk-heavy branches over chasing untouched lines.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Business logic mixed with I/O (DB calls, HTTP) | Untestable, hard to refactor | Extract pure logic into service/domain modules |
| Mutable default arguments (`def f(items=[])`) | Shared state between calls — classic Python gotcha | Use `None` default + create inside function |
| Bare `except:` or `except Exception:` | Swallows `KeyboardInterrupt`, `SystemExit` | Catch specific exceptions |
| No type hints on public API | Hard to understand contracts, no static analysis | Add type hints on function signatures |
| Tests that depend on execution order | Fragile test suite, non-deterministic failures | Each test must be self-contained |
| Forcing async into CPU-bound or simple flows | Adds complexity without throughput benefit | Keep it synchronous unless I/O concurrency is the real bottleneck |
| Mocking internal implementation details | Makes tests brittle and hides real regressions | Mock only true external boundaries |
| Treating line coverage as the goal | Inflates test volume without improving defect detection | Target coverage around changed behavior and risky paths |
| God classes with 10+ methods | Hard to test, hard to reason about | Split by responsibility into focused classes |

## Validation
- `python -m compileall <paths>` (syntax check)
- `pytest tests/` (run tests)
- Lint with project's configured linter.
