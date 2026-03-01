#!/usr/bin/env bash
#
# Purpose: Bootstrap Copilot customization files from a source config root into a target repository `.github` folder.
# Usage examples:
#   ./.github/scripts/bootstrap-copilot-config.sh --target /path/to/repo
#   ./.github/scripts/bootstrap-copilot-config.sh --target /path/to/repo --apply
#   ./.github/scripts/bootstrap-copilot-config.sh --target /path/to/repo --apply --clean
#   ./.github/scripts/bootstrap-copilot-config.sh --target /path/to/repo --apply --include-workflows
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_SOURCE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

SOURCE_DIR="${DEFAULT_SOURCE_DIR}"
TARGET_REPO=""
DRY_RUN=true
CLEAN_SYNC=false
INCLUDE_WORKFLOWS=false
USE_DEFAULT_EXCLUDES=true
EXCLUDE_FILE=""
EXCLUDE_PATTERNS=()

log_info() { echo "ℹ️  $*"; }
log_warn() { echo "⚠️  $*"; }
log_error() { echo "❌ $*" >&2; }
log_success() { echo "✅ $*"; }

usage() {
  cat <<'USAGE'
Usage: bootstrap-copilot-config.sh --target <repo-path> [options]

Options:
  --target <path>          Target repository path (required)
  --source <path>          Source Copilot config root path (default: sibling directory of this script)
  --apply                  Apply changes (default is dry-run)
  --clean                  Remove files in target `.github` that are not in source (requires --apply)
  --include-workflows      Include `.github/workflows/` in synchronization
  --no-default-excludes    Disable default exclusion set
  --exclude <pattern>      Add rsync exclude pattern (repeatable)
  --exclude-file <path>    Read additional exclude patterns from file
  -h, --help               Show help

Notes:
  - Default excludes: `.git/`, `CHANGELOG.md`, `dependabot.yml`, `workflows/`.
  - If `<source>/.bootstrap-ignore` exists, patterns are loaded automatically.
USAGE
}

is_copilot_config_root() {
  local dir="$1"
  [[ -f "${dir}/copilot-instructions.md" && -d "${dir}/instructions" ]]
}

require_dependencies() {
  if ! command -v rsync >/dev/null 2>&1; then
    log_error "Missing dependency: rsync"
    return 1
  fi
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --target)
        TARGET_REPO="${2:-}"
        shift 2
        ;;
      --source)
        SOURCE_DIR="${2:-}"
        shift 2
        ;;
      --apply)
        DRY_RUN=false
        shift
        ;;
      --clean)
        CLEAN_SYNC=true
        shift
        ;;
      --include-workflows)
        INCLUDE_WORKFLOWS=true
        shift
        ;;
      --no-default-excludes)
        USE_DEFAULT_EXCLUDES=false
        shift
        ;;
      --exclude)
        EXCLUDE_PATTERNS+=("${2:-}")
        shift 2
        ;;
      --exclude-file)
        EXCLUDE_FILE="${2:-}"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        log_error "Unknown argument: $1"
        usage
        return 1
        ;;
    esac
  done

  if [[ -z "$TARGET_REPO" ]]; then
    log_error "--target is required"
    return 1
  fi

  if [[ "$CLEAN_SYNC" == true && "$DRY_RUN" == true ]]; then
    log_error "--clean requires --apply"
    return 1
  fi
}

validate_paths() {
  if [[ ! -d "$SOURCE_DIR" ]]; then
    log_error "Source directory not found: $SOURCE_DIR"
    return 1
  fi

  if [[ "$(basename "$SOURCE_DIR")" == ".github" ]]; then
    log_info "Source layout: consumer (.github directory)"
  elif is_copilot_config_root "$SOURCE_DIR"; then
    log_info "Source layout: template (config root directory)"
  else
    log_warn "Source path does not look like a Copilot config root: $SOURCE_DIR"
  fi

  if [[ ! -d "$TARGET_REPO" ]]; then
    log_error "Target repository not found: $TARGET_REPO"
    return 1
  fi

  if [[ -n "$EXCLUDE_FILE" && ! -f "$EXCLUDE_FILE" ]]; then
    log_error "Exclude file not found: $EXCLUDE_FILE"
    return 1
  fi
}

build_rsync_args() {
  RSYNC_ARGS=(-a)

  if [[ "$USE_DEFAULT_EXCLUDES" == true ]]; then
    RSYNC_ARGS+=(--exclude '.git/' --exclude 'CHANGELOG.md' --exclude 'dependabot.yml')
    if [[ "$INCLUDE_WORKFLOWS" != true ]]; then
      RSYNC_ARGS+=(--exclude 'workflows/')
    fi
  fi

  local pattern
  for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    [[ -n "$pattern" ]] && RSYNC_ARGS+=(--exclude "$pattern")
  done

  if [[ -f "${SOURCE_DIR}/.bootstrap-ignore" ]]; then
    RSYNC_ARGS+=(--exclude-from "${SOURCE_DIR}/.bootstrap-ignore")
  fi

  if [[ -n "$EXCLUDE_FILE" ]]; then
    RSYNC_ARGS+=(--exclude-from "$EXCLUDE_FILE")
  fi

  if [[ "$CLEAN_SYNC" == true ]]; then
    RSYNC_ARGS+=(--delete)
  fi

  if [[ "$DRY_RUN" == true ]]; then
    RSYNC_ARGS+=(--dry-run)
  fi
}

run_sync() {
  local target_github_dir="${TARGET_REPO}/.github"
  RSYNC_ARGS=()

  build_rsync_args

  mkdir -p "$target_github_dir"

  log_info "📦 Source: ${SOURCE_DIR}"
  log_info "🎯 Target: ${target_github_dir}"
  log_info "🧪 Mode: $([[ "$DRY_RUN" == true ]] && echo dry-run || echo apply)"
  log_info "🛡️  Default excludes: $([[ "$USE_DEFAULT_EXCLUDES" == true ]] && echo enabled || echo disabled)"
  log_info "📚 Source ignore file: $([[ -f "${SOURCE_DIR}/.bootstrap-ignore" ]] && echo found || echo not-found)"

  rsync "${RSYNC_ARGS[@]}" "${SOURCE_DIR}/" "${target_github_dir}/"

  if [[ "$DRY_RUN" == true ]]; then
    log_success "Dry-run completed. Re-run with --apply to persist changes."
    return 0
  fi

  log_success "Copilot customization bootstrap completed."
  return 0
}

main() {
  require_dependencies || return 1
  parse_args "$@" || return 1
  validate_paths || return 1
  run_sync
}

main "$@"
