---
description: Java project standards with DDD boundaries, readability-first design, and deterministic unit testing.
applyTo: "**/*.java"
---

# Java Instructions

## Mandatory rules
- Treat work as project-oriented (services/modules/components), not script-oriented.
- Apply DDD boundaries: keep domain logic inside domain services/entities/value objects.
- Keep infrastructure details (I/O, SDK calls, persistence wiring) outside core domain logic.
- Use ubiquitous language in class names, methods, and domain-level exceptions.
- Add concise purpose JavaDoc for new/changed core classes when intent is not obvious.
- Use emoji logs for key runtime transitions when logging is touched.
- Prefer early return and guard clauses.
- Prioritize readability and maintainability.
- Add unit tests for testable logic.

## Testing defaults
- Use JUnit 5.
- Use BDD-like naming: `@DisplayName` and `given_when_then`.
- Keep unit tests deterministic and isolated.
- For modify tasks with existing tests: change implementation first, run existing tests, and update tests only for intentional behavior changes.

## Reference implementation
- For code and test examples, use `.github/skills/project-java/SKILL.md`.
