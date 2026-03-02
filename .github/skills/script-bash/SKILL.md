---
name: script-bash
description: Create or modify Bash scripts with purpose header, emoji logs, and readable guard-clause flow.
---

# Bash Script Skill

## When to use
- New Bash scripts.
- Existing Bash scripts that need updates.

## Mandatory rules
- Use Bash (`#!/usr/bin/env bash`), never POSIX `sh`.
- Header must include purpose and usage examples.
- Use emoji logs for runtime states.
- Prefer early return and guard clauses.
- Keep logic straightforward and readable.
- Do not add unit tests unless explicitly requested.

## Minimal template
```bash
#!/usr/bin/env bash
#
# Purpose: {description}
# Usage examples:
#   ./{script_name}.sh --help

set -euo pipefail

log_info() { echo "ℹ️  $*"; }
log_warn() { echo "⚠️  $*"; }
log_success() { echo "✅ $*"; }
log_error() { echo "❌ $*" >&2; }
```

## Validation
- `bash -n`
- `shellcheck -s bash` (if available)
