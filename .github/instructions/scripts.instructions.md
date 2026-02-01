---
applyTo: "scripts/**"
---

# Scripts Instructions

## terraform.sh Wrapper

The main script for Terraform operations:

```bash
./terraform.sh plan|apply|destroy
```

### Conventions

- Use wrapper instead of direct `terraform` commands
- Wrapper handles backend configuration
- Wrapper sets correct subscription context

## Bash Scripts

### Template

```bash
#!/bin/bash
# ==============================================================================
# Script Name: script-name.sh
# Description: Brief description
# Usage: ./script-name.sh [options]
# ==============================================================================

set -euo pipefail

log_info() { echo "🔍 [INFO] $*"; }
log_success() { echo "✅ [SUCCESS] $*"; }
log_error() { echo "❌ [ERROR] $*" >&2; }
```

### Error Handling

- Use `set -euo pipefail`
- Quote all variables
- Handle Azure CLI errors gracefully
