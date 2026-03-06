#!/usr/bin/env bash
# ==============================================================================
# Script Name: cleanup-terraform-dirs.sh
# Description: Remove .terraform directories from all folders containing *.tf files
# Usage: ./scripts/cleanup-terraform-dirs.sh [--dry-run] [ROOT_DIR]
# ==============================================================================

set -euo pipefail

log_info() { echo "🔍 [INFO] $*"; }
log_warn() { echo "⚠️ [WARN] $*"; }
log_success() { echo "✅ [SUCCESS] $*"; }
log_error() { echo "❌ [ERROR] $*" >&2; }

usage() {
  cat <<'EOF'
Usage:
  ./scripts/cleanup-terraform-dirs.sh [--dry-run] [ROOT_DIR]

Options:
  --dry-run, -n   Show what would be removed without deleting anything
  --help, -h      Show this help message

Examples:
  ./scripts/cleanup-terraform-dirs.sh
  ./scripts/cleanup-terraform-dirs.sh --dry-run
  ./scripts/cleanup-terraform-dirs.sh /path/to/repo
EOF
}

DRY_RUN="false"
ROOT_DIR="."

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run|-n)
      DRY_RUN="true"
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      if [ "$ROOT_DIR" != "." ]; then
        log_error "Only one ROOT_DIR can be specified."
        usage
        exit 1
      fi
      ROOT_DIR="$1"
      ;;
  esac
  shift
done

if [ ! -d "$ROOT_DIR" ]; then
  log_error "ROOT_DIR does not exist: $ROOT_DIR"
  exit 1
fi

ROOT_DIR="$(cd "$ROOT_DIR" && pwd -P)"
TMP_FILE="$(mktemp)"
trap 'rm -f "$TMP_FILE"' EXIT

log_info "Scanning Terraform directories under: $ROOT_DIR"

find "$ROOT_DIR" \
  -type f -name '*.tf' \
  -not -path '*/.terraform/*' \
  -not -path '*/.git/*' \
  -exec dirname {} \; | sort -u > "$TMP_FILE"

total_tf_dirs=0
removed_count=0
found_terraform_dirs=0

while IFS= read -r dir; do
  [ -z "$dir" ] && continue
  total_tf_dirs=$((total_tf_dirs + 1))

  terraform_cache_dir="$dir/.terraform"
  if [ -d "$terraform_cache_dir" ]; then
    found_terraform_dirs=$((found_terraform_dirs + 1))

    if [ "$DRY_RUN" = "true" ]; then
      log_info "[DRY-RUN] Would remove: $terraform_cache_dir"
    else
      rm -rf "$terraform_cache_dir"
      log_info "Removed: $terraform_cache_dir"
    fi
    removed_count=$((removed_count + 1))
  fi
done < "$TMP_FILE"

if [ "$found_terraform_dirs" -eq 0 ]; then
  log_warn "No .terraform directories found in Terraform folders."
fi

if [ "$DRY_RUN" = "true" ]; then
  log_success "Dry-run completed. Terraform folders scanned: $total_tf_dirs, .terraform matches: $removed_count"
else
  log_success "Cleanup completed. Terraform folders scanned: $total_tf_dirs, .terraform removed: $removed_count"
fi
