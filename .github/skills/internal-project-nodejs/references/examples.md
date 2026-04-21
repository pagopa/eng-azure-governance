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

## Minimal package.json Example

```json
{
  "name": "example-service",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "node --test",
    "typecheck": "tsc --noEmit"
  },
  "engines": {
    "node": ">=22"
  }
}
```

## Minimal tsconfig.json Example

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*.ts", "tests/**/*.ts"]
}
```
