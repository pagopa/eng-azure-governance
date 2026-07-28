---
description: Node.js project standards with DDD-oriented layering, early returns, and deterministic test practices.
applyTo: "**/*.js,**/*.cjs,**/*.mjs,**/*.ts,**/*.tsx,**/package.json,**/tsconfig.json"
excludeAgent: "cloud-agent"
---

# Node.js and TypeScript Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify domain and adapter boundaries remain explicit and not cross-coupled.
- Flag unhandled async errors, floating promises, or unsafe process exits.
- Check API and type contract changes for compatibility impact.
- Verify tests cover changed logic and avoid nondeterministic timing.
- Report dependency additions or version drift with unnecessary blast radius.
- Check `package.json` and `tsconfig.json` changes for build/runtime contract drift.
- Flag complex branching where guard clauses would reduce risk.
