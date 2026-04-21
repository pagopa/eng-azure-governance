---
name: internal-spring-boot-development
description: Use when Spring Boot framework choices drive the work, such as controllers, configuration properties, repositories, scheduled jobs, or Spring-specific tests.
---

# Internal Spring Boot Development

Follow `.github/instructions/internal-java.instructions.md` for the baseline Java rules. Use this skill only when the Spring Boot framework choices materially affect the design, wiring, testing, or configuration.

## When to use

- Spring Boot framework choices drive the work, such as controllers, configuration properties, repositories, scheduled jobs, or Spring-specific tests.
- The task depends on Spring wiring, stereotypes, test slices, or Boot configuration behavior rather than plain Java structure alone.
- You need Spring-specific guidance after the general Java ownership boundary is already clear.

## Workflow

1. Identify the Spring surface first.
   Decide whether the task is primarily HTTP, persistence, configuration, scheduled/background work, or testing. Keep the rest of the framework out of scope unless the change truly crosses boundaries.
2. Keep the framework at the edge.
   Map transport, persistence, and scheduling concerns in Spring-managed classes, but keep business rules in plain services or collaborators that remain easy to test.
3. Prefer explicit wiring over annotation sprawl.
   Use constructor injection, typed configuration, focused stereotypes, and narrow transaction boundaries instead of scattering framework behavior across many classes.
4. Choose the lightest Spring test that proves the behavior.
   Start with unit tests or Spring test slices. Escalate to `@SpringBootTest` only when container wiring is the thing under test.

## Default Spring Boot Rules

- Keep controllers thin: validate input, map transport types, delegate once, and return response DTOs.
- Keep services stateless and focused on business behavior; avoid mutable singleton state.
- Bind structured settings with `@ConfigurationProperties` instead of scattering `@Value` keys.
- Validate request DTOs with Bean Validation and `@Valid`.
- Centralize API error mapping with `@ControllerAdvice` or the project's existing equivalent.
- Keep transaction boundaries in the service layer and scope them only around the behavior that needs atomicity.
- Do not leak JPA entities directly through HTTP contracts unless the project already made that tradeoff intentionally.

## References

- Load `references/http-config.md` when the task is mainly about controllers, request/response DTOs, validation, exception mapping, or application configuration.
- Load `references/testing-and-data.md` when the task is mainly about repositories, transactions, test slices, containerized integration tests, or data-access boundaries.

## Guardrails

- Do not turn every helper into a Spring bean; plain classes are fine when the framework adds no value.
- Do not choose YAML vs properties by doctrine; follow the existing project format unless the user asked for a migration.
- Do not default to `@SpringBootTest` for controller or repository work that a slice test can cover faster.
- Do not hide framework misconfiguration with defensive fallbacks that make failures harder to detect.
- Read current Spring Boot documentation when the recommendation depends on framework behavior, annotation semantics, or test-slice support that may have changed across releases.

## Validation

- Run the project's existing Java build and test command after changes.
- Prefer `./mvnw test`, `mvn test`, `./gradlew test`, or the checked-in equivalent over generic guesses.
