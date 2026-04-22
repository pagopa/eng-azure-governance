---
name: internal-project-nodejs
description: Use when creating or modifying Node.js or TypeScript project code such as services, APIs, middleware, or modules, and the main concern is application code rather than Docker, workflows, or infrastructure.
---

# Node.js Project Skill

Follow `.github/instructions/internal-nodejs.instructions.md` for the baseline Node.js rules. This skill adds project-specific guidance only.

## When to use

- Services, handlers, adapters, and utility modules.
- Refactoring or extending existing Node.js components.

## Project-specific guidance

- Follow the existing module system and runtime constraints before introducing ESM/CJS or build-tool changes.
- Validate inputs at API or function boundaries and keep async error handling explicit.
- Keep framework wiring thin and move request-shaping logic out of transport handlers when reuse or testing would improve.

Load `references/examples.md` when you need a minimal module or test example.

## Test stack

- Follow the repository test-stack defaults from the instruction owner.
- If the repository already uses Jest, stay with local Jest conventions instead of introducing mixed test stacks.
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.

## Runtime and async guidance

- Prefer `async`/`await` over promise chains unless streaming or concurrency composition clearly benefits from lower-level primitives.
- Use `Promise.all` only for independent work; use `Promise.allSettled` when partial failure is acceptable.
- Keep CPU-heavy work off request paths or move it to worker threads or an external service.
- Choose framework and runtime patterns from the repository first; do not switch to Fastify, NestJS, Bun, or another stack without an explicit reason.
- Default to the current module system. Use ESM for new projects only when the repo and toolchain already support it cleanly.

## Testing guidance

- Prefer unit tests and narrow integration tests over broad end-to-end coverage for every module change.
- In Jest repos, use focused mocks and reset them between tests; do not introduce Jest where the project already standardizes on `node:test`.
- Keep async tests explicit with `await`, `assert.rejects`, or the framework-native async helpers.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Mixing async/sync without `await` | Unhandled promise rejections, silent failures | Always `await` async calls; use `async` on the function |
| Business logic inside route handlers | Untestable, coupled to Express/framework | Extract to service modules, inject dependencies |
| Using `var` instead of `const`/`let` | Hoisting bugs, scope confusion | Use `const` by default, `let` only when reassignment is needed |
| Bare `catch(err) {}` that swallows errors | Silent failures, impossible to debug | Log the error and rethrow, or handle specifically |
| No input validation on API boundaries | Runtime crashes on malformed input | Validate and fail fast at handler entry |
| Callback-style code in modern Node.js | Hard to read, callback hell | Use async/await with Promises |
| Mixing Jest and `node:test` in the same project without reason | Duplicated conventions and confusing tooling | Follow the test stack already used by the repository |
| Changing module system casually | Breaks tooling, imports, and runtime behavior | Stay with the existing ESM/CJS choice unless the migration is explicit |
| Using `Promise.all` on dependent work | Masks ordering assumptions and makes failures harder to interpret | Keep dependent async steps sequential |

## Validation

- Run tests: `node --test` or `npm test`.
- Lint: `npx eslint .` when configured.
- Type check: `npx tsc --noEmit` for TypeScript projects.
