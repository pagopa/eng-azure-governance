# Persistence, Transactions, and Testing

Load this file when the Spring Boot task is mainly about repositories, transactions, database integration, or test strategy.

## Data Boundaries

| Problem | Prefer | Avoid |
| --- | --- | --- |
| HTTP layer needs data | Map entities to DTOs or dedicated view models | Returning entities directly unless already established |
| Repository abstraction | Spring Data repositories or small project-local interfaces | Business logic embedded in repository or controller layers |
| Transaction scope | Service-layer `@Transactional` on the narrow behavior that must be atomic | Broad class-level transactions applied by habit |

## Test Selection

| Goal | Prefer | Escalate only when |
| --- | --- | --- |
| Pure business logic | Plain unit tests with mocked collaborators | Spring wiring itself changes behavior |
| MVC endpoint behavior | `@WebMvcTest` | Security, converters, or full application wiring must be proven together |
| JPA mapping/query behavior | `@DataJpaTest` | The database integration depends on infrastructure outside the slice |
| Full application behavior | `@SpringBootTest` | Cross-cutting configuration or bootstrap is the thing being verified |

## Integration Guidance

- Use Testcontainers when the behavior depends on a real database or external service contract.
- Keep fixture setup explicit and local to the test when possible.
- Preserve existing package structure and test conventions before adding new patterns.
