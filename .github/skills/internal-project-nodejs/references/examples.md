# Node.js Project Examples

## Minimal Module Example

```javascript
/** Purpose: Build a user profile response. */
function buildUserProfile(input) {
  if (!input?.id) {
    throw new Error("❌ id is required");
  }
  return { id: input.id, name: input.name ?? "unknown" };
}
```

## Minimal Test Example

```javascript
const test = require("node:test");
const assert = require("node:assert/strict");

test("given missing id when building profile then throws", () => {
  assert.throws(() => buildUserProfile({}), /id is required/);
});
```
