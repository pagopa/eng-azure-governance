---
description: Java project standards with DDD boundaries, readability-first design, and deterministic unit testing.
applyTo: "**/*.java,**/pom.xml,**/build.gradle,**/build.gradle.kts"
---

# Java Instructions

## Mandatory rules

- Treat work as project-oriented (services/modules/components), not script-oriented.
- Keep business logic separated from I/O and infrastructure concerns (SDK calls, persistence, external APIs).
- Use clear, domain-relevant naming in class names, methods, and exceptions.
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

- For code and test examples, use `.github/skills/internal-project-java/SKILL.md`.

## Build-file boundary

- For `pom.xml`, `build.gradle`, and `build.gradle.kts`, keep guidance limited to dependency intent, plugin clarity, and test/runtime alignment.
- Do not use this instruction to restate full Maven or Gradle style guidance that belongs in a narrower build-tool owner.
