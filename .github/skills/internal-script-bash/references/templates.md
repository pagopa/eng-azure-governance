# Bash Script Templates

Use this reference when you need a starter script, a CLI parsing pattern, or the standard cleanup helpers.

## Minimal Template

```bash
#!/usr/bin/env bash
#
# Purpose: {description}
# Usage examples:
#   ./{script_name}.sh
#   ./{script_name}.sh --help
#   ./{script_name}.sh --target custom-target

set -euo pipefail

DEFAULT_TARGET="default-target"

log_info()    { echo "ℹ️  $*"; }
log_warn()    { echo "⚠️  $*"; }
log_success() { echo "✅ $*"; }
log_error()   { echo "❌ $*" >&2; }

main() {
  local target="$DEFAULT_TARGET"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --target) target="${2:?❌ --target requires a value}"; shift 2 ;;
      --help) usage; exit 0 ;;
      *) log_error "Unknown option: $1"; usage; exit 1 ;;
    esac
  done

  log_info "Processing $target"
  # ... logic ...
  log_success "Done"
}

usage() {
  cat <<'EOF'
Usage:
  ./{script_name}.sh [--target value]
EOF
}

main "$@"
```

## Argument Parsing Pattern

```bash
DEFAULT_SCOPE="repo"
SCOPE="$DEFAULT_SCOPE"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)  SCOPE="${2:?❌ --scope requires a value}"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    --help)   usage; exit 0 ;;
    *)        log_error "Unknown option: $1"; usage; exit 1 ;;
  esac
done
```

## Hardening Helpers

```bash
require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    log_error "Missing required command: $1"
    exit 1
  }
}

cleanup() {
  [[ -n "${TMP_DIR:-}" && -d "$TMP_DIR" ]] || return 0
  rm -rf -- "$TMP_DIR"
}

TMP_DIR="$(mktemp -d)"
trap cleanup EXIT
```
