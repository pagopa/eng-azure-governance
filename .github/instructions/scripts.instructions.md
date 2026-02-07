---
applyTo: "**/*.sh,**/*.py"
---

# Script Instructions

## Cross-language rules
- Start with purpose and usage examples.
- Use early return and guard clauses.
- Keep logs and user-facing output in English.
- Prefer readability over compact or clever code.

## Bash-specific
- Use `#!/usr/bin/env bash`.
- Use `set -euo pipefail`.

## Python-specific
- Use type hints for function signatures.
- Add tests for testable logic.
- Pin dependencies in `requirements.txt` when external libraries are required.
