# HTTP, Validation, and Configuration

Load this file when the Spring Boot task is mostly about controllers, API contracts, validation, exception handling, or application settings.

## Endpoint Design

| Concern | Prefer | Avoid |
| --- | --- | --- |
| Request mapping | Dedicated request/response DTOs with framework annotations at the edge | Reusing JPA entities as HTTP payloads by default |
| Validation | Bean Validation on DTOs plus `@Valid` at the entry point | Ad hoc null and size checks spread through service code |
| Error responses | One consistent exception-mapping layer such as `@ControllerAdvice` | Repeating `try/catch` blocks in each controller |
| Logging | Log business-significant failures once with useful context | Logging and rethrowing the same exception in multiple layers |

## Configuration

| Need | Prefer | Avoid |
| --- | --- | --- |
| Structured settings | `@ConfigurationProperties` with validation | Scattered `@Value` fields for every property |
| Secrets | External secret stores or environment-driven injection | Hardcoded secrets or checked-in defaults |
| Environment differences | Existing profile or configuration layering already used by the project | Creating new profiles or property sources unless the task requires them |

## Practical Cues

- Keep request validation at the boundary so service methods can assume valid inputs.
- Treat missing configuration as a startup failure unless the user explicitly asked for optional behavior.
- Follow the existing JSON error envelope or problem-details format instead of inventing a new one mid-task.
