---
applyTo: "**/*.sh"
---

# Bash Instructions

## Mandatory rules
- Use Bash only: `#!/usr/bin/env bash`.
- Add a header comment with purpose and usage examples.
- Use emoji logs (`ℹ️ ✅ ⚠️ ❌`) for runtime visibility.
- Prefer early return and simple, readable functions.
- Apply these rules for both create and modify operations.

## Standard skeleton
```bash
#!/usr/bin/env bash
#
# Purpose: Explain what this script does.
# Usage examples:
#   ./script.sh --help
#   ./script.sh --input data.json

set -euo pipefail
```

## Best practices
- Quote variables (`"$var"`).
- Use `[[ ... ]]` and `$(...)`.
- Check dependencies with `command -v`.
- Keep functions short and focused.

## Validation
- `bash -n <script>.sh`
- `shellcheck -s bash <script>.sh` (if available)
