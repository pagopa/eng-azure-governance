# Java Project Examples

## Minimal Class Example

```java
/** Purpose: Resolve user by id with input validation. */
public final class UserService {
    public String resolveUserId(String userId) {
        if (userId == null || userId.isBlank()) {
            throw new IllegalArgumentException("❌ userId is required");
        }
        return userId.trim();
    }
}
```

## Minimal Test Example

```java
import static org.junit.jupiter.api.Assertions.assertThrows;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class UserServiceTest {
    @Test
    @DisplayName("given blank userId when resolving then throws")
    void givenBlankUserId_whenResolving_thenThrows() {
        var service = new UserService();
        assertThrows(IllegalArgumentException.class, () -> service.resolveUserId(" "));
    }
}
```
