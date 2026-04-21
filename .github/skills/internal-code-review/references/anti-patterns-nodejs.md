# Node.js / TypeScript Anti-Patterns

Reference: `instructions/internal-nodejs.instructions.md`

## Critical

| ID | Anti-pattern | Why |
|---|---|---|
| ND-C01 | Hardcoded secrets, tokens, or passwords | Credential exposure risk |
| ND-C02 | `eval()` or `new Function()` on untrusted input | Arbitrary code execution |
| ND-C03 | User input in `child_process.exec()` without sanitization | Command injection |

## Major

| ID | Anti-pattern | Why |
|---|---|---|
| ND-M01 | Unhandled promise rejection (missing `.catch()` or `try/catch` on `await`) | Silent crash or process exit |
| ND-M02 | Synchronous file I/O (`readFileSync`) in request path | Event loop blocking |
| ND-M03 | Missing `AbortController` or timeout on outbound HTTP/fetch | Unbounded resource consumption |
| ND-M04 | `any` type used without justification in TypeScript | Type safety erosion |
| ND-M05 | Missing error handling on stream/event emitter `error` events | Uncaught exception crash |
| ND-M06 | `console.log` in application/library code instead of structured logger | No log level control |
| ND-M07 | Missing unit tests for new exported functions | Coverage mandate |
| ND-M08 | Callback-based patterns where async/await is available | Readability and error propagation |

## Minor

| ID | Anti-pattern | Why |
|---|---|---|
| ND-m01 | Unused imports or variables | Dead code noise |
| ND-m02 | Missing purpose comment on exported modules | Discoverability gap |
| ND-m03 | `require()` in ESM context or mixed module systems | Import consistency |
| ND-m04 | `// @ts-ignore` without inline justification | Hides real issues |
| ND-m05 | Dead code (unreachable branches, commented-out blocks) | Maintenance burden |
| ND-m06 | Event listener without corresponding cleanup/removal | Memory leak risk |

## Nit

| ID | Anti-pattern | Why |
|---|---|---|
| ND-N01 | Non-standard naming (camelCase for functions, PascalCase for classes/types) | Convention consistency |
| ND-N02 | Missing trailing newline at end of file | POSIX convention |
| ND-N03 | Inconsistent use of semicolons within a project | Style consistency |
| ND-N04 | Import order not organized (node builtins → third-party → local) | Convention |

## Good vs bad examples

```typescript
// BAD (ND-M01): unhandled rejection
async function fetchUser(id: string) {
  const res = await fetch(`/api/users/${id}`);
  return res.json();
}

// GOOD: error handling + timeout
async function fetchUser(id: string): Promise<User> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);
  try {
    const res = await fetch(`/api/users/${id}`, { signal: controller.signal });
    if (!res.ok) throw new Error(`⚠️ User fetch failed: ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(timeout);
  }
}
```

```javascript
// BAD (ND-M02): blocking the event loop
const data = fs.readFileSync('/path/to/file');
processRequest(data);

// GOOD: async I/O
const data = await fs.promises.readFile('/path/to/file');
processRequest(data);
```
