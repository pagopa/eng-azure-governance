---
applyTo: "**/*.java"
---

# Java Instructions

## Mandatory rules
- Treat work as project-oriented (services/modules/components), not script-oriented.
- Add concise purpose JavaDoc for new/changed core classes when intent is not obvious.
- Use emoji logs for key runtime transitions when logging is touched.
- Prefer early return and guard clauses.
- Prioritize readability and maintainability.
- Add unit tests for testable logic.

## Minimal class example
```java
/** Purpose: Validate and normalize user input. */
public final class UserService {
    public String normalizeUserId(String userId) {
        if (userId == null || userId.isBlank()) {
            throw new IllegalArgumentException("❌ userId is required");
        }
        return userId.trim().toLowerCase();
    }
}
```

## Testing defaults
- Use JUnit 5.
- Use BDD-like naming: `@DisplayName` and `given_when_then`.
- Keep unit tests deterministic and isolated.

## Minimal test example
```java
import static org.junit.jupiter.api.Assertions.assertThrows;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class UserServiceTest {
    @Test
    @DisplayName("given blank userId when normalize then throws")
    void givenBlankUserId_whenNormalize_thenThrows() {
        var service = new UserService();
        assertThrows(IllegalArgumentException.class, () -> service.normalizeUserId(" "));
    }
}
```
