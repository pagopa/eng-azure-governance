---
applyTo: "**/Makefile,**/*.mk"
---

# Makefile Instructions

## Conventions
- Use lowercase, hyphenated target names.
- Mark non-file targets with `.PHONY`.
- Keep commands deterministic and readable.

## Recommended patterns
- Provide a `help` target.
- Centralize common variables near the top.
- Avoid hidden side effects in default targets.

## Output
- Keep runtime output in English.
- Use clear success/error messages.
