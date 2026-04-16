---
name: internal-project-java
description: Use when creating or modifying Java project code and the main concern is Java application structure, tests, or library/service design rather than Spring Boot framework choices.
---

# Java Project Skill

Follow `.github/instructions/internal-java.instructions.md` for the baseline Java rules. This skill adds project-specific guidance only.

## When to use
- Services, handlers, controllers, utilities, modules.
- Refactoring or extending existing Java components.

## Project-specific guidance
- Prefer constructor injection and immutable dependencies in Spring components.
- Keep controllers thin, services stateless, and API DTOs separate from persistence entities.
- Use Java 21 features only when the project already targets them or the runtime requirement is explicit.

Load `references/examples.md` when you need a minimal class or test example.

## Test stack
- Follow the JUnit 5 defaults from the instruction owner.
- Use `@ParameterizedTest`, `assertAll`, `@Nested`, and `@Tag` when they improve test clarity rather than just adding ceremony.
- Use Spring test slices such as `@WebMvcTest` or `@DataJpaTest` before defaulting to full-context tests.
- Use Testcontainers when integration tests need real databases or external dependencies.
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

## Spring coordination
- Keep Spring-specific design decisions lightweight here and treat controller, configuration, repository, or test-slice-heavy work as a separate framework-focused lane.
- Prefer constructor injection with `private final` dependencies and keep transaction boundaries narrow.

## Modern Java guidance
- Prefer records for small immutable data carriers when the codebase already uses them.
- Use sealed hierarchies only when bounded polymorphism is a real domain constraint.
- Consider virtual threads for high-concurrency I/O-heavy flows only when the framework and blocking model are understood.
- Reach for Testcontainers and profiling before speculative JVM tuning.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Business logic inside controller/handler | Untestable, tightly coupled to framework | Extract to a service class, inject via constructor |
| Catching `Exception` everywhere | Swallows unexpected errors, hides bugs | Catch specific exceptions; let runtime errors propagate |
| Mutable shared state in service classes | Thread-safety bugs in concurrent environments | Use immutable objects or proper synchronization |
| No null checks on external input | NullPointerException at runtime | Validate at entry point with guard clauses |
| Test names like `test1`, `testMethod` | No documentation value, hard to diagnose failures | Use `given_when_then` naming with `@DisplayName` |
| Full `@SpringBootTest` for every test | Slow feedback and blurred failure scope | Prefer unit tests or Spring test slices first |
| Exposing JPA entities directly from controllers | Leaks persistence shape into the API and couples layers | Map entities to request/response DTOs |
| Adding virtual threads without checking execution model | Can mask blocking or context propagation issues | Adopt them only when runtime support and workload fit are clear |
| Over-using inheritance for code reuse | Rigid hierarchies, fragile base class problem | Prefer composition and delegation |

## Validation
- Compile with `mvn compile` or `gradle build`.
- Run tests with `mvn test` or `gradle test`.
- Check code style with project linter when available.
