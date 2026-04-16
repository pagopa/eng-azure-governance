# Versioning Strategy

Use versioning to communicate compatibility, not as a substitute for SHA pinning.

## Rules

- Treat the full commit SHA as the immutable security pin in caller workflows.
- Use release tags as human-readable labels and move major tags only within a compatibility line.
- Cut a new major when inputs, outputs, required tools, or externally visible behavior break callers.
- Keep deprecated inputs or outputs long enough for callers to migrate when practical.
- Document compatibility and migration notes in the action README and release notes.
- When publishing examples, pair the human tag with the pinned SHA in comments instead of telling callers to pin only the tag.

## Compatibility questions before release

- Can existing callers keep the same `with:` block?
- Do output names and meanings stay the same?
- Are failure messages or side effects materially different?
- Does the action now require extra permissions or tools on the runner?

If the answer to any of these is no, treat the change as a versioning event rather than a silent cleanup.
