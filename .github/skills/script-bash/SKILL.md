---
name: script-bash
description: Guide for creating or modifying Bash scripts in this repository. Use when asked to write or update simple operational scripts.
---

# Create Bash Script

## Context

I need to create a Bash script for simple operations in Azure governance management.

## Input Required

- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}

## Mandatory Template

```bash
#!/usr/bin/env bash
#
# 📋 {script_name}.sh
# 🎯 Purpose: {purpose}
# 📖 Usage: ./src/scripts/{script_name}.sh [options]
#

set -euo pipefail

log_info()    { echo -e "🔍 $1"; }
log_success() { echo -e "✅ $1"; }
log_error()   { echo -e "❌ $1" >&2; }

main() {
    log_info "Starting script"
    # Early return pattern
    # ... implementation ...
    log_success "Completed"
}

main "$@"
```

## References

Follow conventions in `#file:.github/copilot-instructions.md`
