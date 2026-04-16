# Java Anti-Patterns

Reference: `instructions/internal-java.instructions.md`

## Critical
| ID | Anti-pattern | Why |
|---|---|---|
| JV-C01 | Hardcoded secrets, tokens, or passwords | Credential exposure risk |
| JV-C02 | Deserialization of untrusted data (`ObjectInputStream`) | Remote code execution risk |
| JV-C03 | SQL string concatenation instead of parameterized queries | SQL injection |

## Major
| ID | Anti-pattern | Why |
|---|---|---|
| JV-M01 | Bare `catch (Exception e)` that swallows without re-throw or logging | Silent failures |
| JV-M02 | Missing `try-with-resources` for `AutoCloseable` | Resource leak |
| JV-M03 | Mutable shared state without synchronization | Race conditions |
| JV-M04 | `null` return from public methods without `@Nullable` or `Optional` | NullPointerException traps |
| JV-M05 | Method body longer than 40 lines | Complexity and testability concern |
| JV-M06 | Missing unit tests for new public methods | Coverage mandate |
| JV-M07 | Raw types or unchecked casts without justification | Type safety erosion |
| JV-M08 | `System.out.println` in application/library code | No log level control |

## Minor
| ID | Anti-pattern | Why |
|---|---|---|
| JV-m01 | Unused imports | Dead code noise |
| JV-m02 | Missing purpose JavaDoc on public classes | Discoverability gap |
| JV-m03 | Field injection (`@Autowired` on fields) instead of constructor injection | Testability and immutability |
| JV-m04 | `@SuppressWarnings` without inline justification | Hides real issues |
| JV-m05 | Dead code (unreachable branches, commented-out blocks) | Maintenance burden |
| JV-m06 | Mutable collections returned from public API without wrapping | Encapsulation leak |

## Nit
| ID | Anti-pattern | Why |
|---|---|---|
| JV-N01 | Non-standard naming (camelCase for methods, PascalCase for classes) | Convention consistency |
| JV-N02 | Missing trailing newline at end of file | POSIX convention |
| JV-N03 | Inconsistent brace style within a file | Style consistency |
| JV-N04 | Import not organized (java → javax → third-party → project) | Convention |

## Good vs bad examples

```java
// BAD (JV-M02): resource leak
public String readFile(Path path) throws IOException {
    BufferedReader reader = new BufferedReader(new FileReader(path.toFile()));
    return reader.readLine();
}

// GOOD: try-with-resources
public String readFile(Path path) throws IOException {
    try (var reader = new BufferedReader(new FileReader(path.toFile()))) {
        return reader.readLine();
    }
}
```

```java
// BAD (JV-M04): null return trap
public User findUser(String id) {
    return userMap.get(id);
}

// GOOD: Optional return
public Optional<User> findUser(String id) {
    return Optional.ofNullable(userMap.get(id));
}
```
