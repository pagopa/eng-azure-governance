#!/usr/bin/env bash
#
# Purpose: Validate Copilot customization files under .github.
# Usage examples:
#   ./.github/scripts/validate-copilot-customizations.sh
#   ./.github/scripts/validate-copilot-customizations.sh --scope root --mode strict
#   ./.github/scripts/validate-copilot-customizations.sh --scope all --mode legacy-compatible
#   ./.github/scripts/validate-copilot-customizations.sh --scope repo=my-repo --mode legacy-compatible
#

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
readonly ROOT_DIR

MODE="strict"
SCOPE="root"
REPORT_FORMAT="text"
REPORT_FILE=""

FAILURES=0
WARNINGS=0

log_info() { echo "ℹ️  $*"; }
log_warn() { echo "⚠️  $*"; }
log_error() { echo "❌ $*" >&2; }
log_success() { echo "✅ $*"; }

usage() {
  cat << 'USAGE'
Usage: validate-copilot-customizations.sh [--scope root|all|repo=<name>] [--mode strict|legacy-compatible] [--report text|json] [--report-file <path>]

Options:
  --scope   Validation scope (default: root)
            root            Validate only workspace root .github
            all             Validate root + all immediate sub-repos that contain .github
            repo=<name>     Validate root + one specific sub-repo (e.g., repo=my-repo)

  --mode    Validation profile (default: strict)
            strict              Enforce full current standard
            legacy-compatible   Allow legacy prompt conventions with warnings

  --report       Report output format (default: text)
                 text                Human-readable logs only
                 json                Human-readable logs + JSON summary file

  --report-file  JSON report file path (required when --report json)

  -h, --help  Show this help message
USAGE
}

record_error() {
  local msg="$1"
  log_error "$msg"
  FAILURES=$((FAILURES + 1))
}

record_warn() {
  local msg="$1"
  log_warn "$msg"
  WARNINGS=$((WARNINGS + 1))
}

record_issue() {
  local severity="$1"
  local msg="$2"

  if [[ "$severity" == "error" ]]; then
    record_error "$msg"
  else
    record_warn "$msg"
  fi
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --mode)
        MODE="${2:-}"
        shift 2
        ;;
      --scope)
        SCOPE="${2:-}"
        shift 2
        ;;
      --report)
        REPORT_FORMAT="${2:-}"
        shift 2
        ;;
      --report-file)
        REPORT_FILE="${2:-}"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        record_error "Unknown argument: $1"
        usage
        exit 1
        ;;
    esac
  done

  case "$MODE" in
    strict|legacy-compatible)
      ;;
    *)
      record_error "Invalid mode '${MODE}'. Use strict or legacy-compatible."
      exit 1
      ;;
  esac

  case "$SCOPE" in
    root|all|repo=*)
      ;;
    *)
      record_error "Invalid scope '${SCOPE}'. Use root, all, or repo=<name>."
      exit 1
      ;;
  esac

  case "$REPORT_FORMAT" in
    text|json)
      ;;
    *)
      record_error "Invalid report format '${REPORT_FORMAT}'. Use text or json."
      exit 1
      ;;
  esac

  if [[ "$REPORT_FORMAT" == "json" && -z "$REPORT_FILE" ]]; then
    record_error "--report-file is required when --report json is used."
    exit 1
  fi
}

json_escape() {
  local raw="$1"
  raw="${raw//\\/\\\\}"
  raw="${raw//\"/\\\"}"
  raw="${raw//$'\n'/\\n}"
  printf '%s' "$raw"
}

write_json_report() {
  local status="$1"
  local timestamp
  local payload

  [[ "$REPORT_FORMAT" == "json" ]] || return 0

  timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

  payload="$(cat <<EOF
{
  "status": "$(json_escape "$status")",
  "mode": "$(json_escape "$MODE")",
  "scope": "$(json_escape "$SCOPE")",
  "failures": ${FAILURES},
  "warnings": ${WARNINGS},
  "timestamp_utc": "$(json_escape "$timestamp")"
}
EOF
)"

  mkdir -p "$(dirname "$REPORT_FILE")"
  printf '%s\n' "$payload" > "$REPORT_FILE"
  log_info "🧾 JSON report written to ${REPORT_FILE}"
}

frontmatter() {
  awk '
    NR == 1 && $0 == "---" { in_fm = 1; next }
    in_fm && $0 == "---" { exit }
    in_fm { print }
  ' "$1"
}

has_key() {
  local file="$1"
  local key="$2"
  frontmatter "$file" | grep -Eq "^${key}:[[:space:]]*.+$"
}

has_heading_exact() {
  local file="$1"
  local heading="$2"
  grep -Eq "^${heading}$" "$file"
}

has_heading_regex() {
  local file="$1"
  local regex="$2"
  grep -Eq "$regex" "$file"
}

check_required_keys() {
  local file="$1"
  local severity="$2"
  shift 2
  local key

  for key in "$@"; do
    if ! has_key "$file" "$key"; then
      record_issue "$severity" "Missing frontmatter key '${key}': ${file}"
    fi
  done
}

check_optional_keys() {
  local file="$1"
  shift
  local key

  for key in "$@"; do
    if ! has_key "$file" "$key"; then
      record_warn "Recommended frontmatter key '${key}' is missing: ${file}"
    fi
  done
}

prompt_skill_refs() {
  local file="$1"
  grep -oE '\.github/skills/[A-Za-z0-9._/-]+/SKILL\.md' "$file" | sort -u || true
}

validate_prompt_file() {
  local file="$1"
  local base_dir="$2"
  local severity="error"
  local section_severity="error"
  local refs=()
  local ref

  if [[ "$MODE" == "strict" ]]; then
    check_required_keys "$file" error description name agent argument-hint
  else
    check_required_keys "$file" error description agent
    check_optional_keys "$file" name argument-hint
    section_severity="warn"
  fi

  if frontmatter "$file" | grep -Eq '^mode:[[:space:]]*'; then
    severity="error"
    [[ "$MODE" == "legacy-compatible" ]] && severity="warn"
    record_issue "$severity" "Legacy prompt key 'mode' found: ${file}"
  fi

  if ! has_heading_exact "$file" '## Instructions'; then
    record_issue "$section_severity" "Prompt missing '## Instructions' section: ${file}"
  fi

  if [[ "$MODE" == "strict" ]]; then
    if ! has_heading_exact "$file" '## Validation'; then
      record_issue error "Prompt missing '## Validation' section: ${file}"
    fi
    if ! has_heading_exact "$file" '## Minimal example'; then
      record_issue error "Prompt missing '## Minimal example' section: ${file}"
    fi
  else
    if ! has_heading_regex "$file" '^## (Validation|Validations)$'; then
      record_warn "Prompt missing '## Validation'/'## Validations' section: ${file}"
    fi
    if ! has_heading_exact "$file" '## Minimal example'; then
      record_warn "Prompt missing '## Minimal example' section: ${file}"
    fi
  fi

  while IFS= read -r ref; do
    [[ -n "$ref" ]] && refs+=("$ref")
  done < <(prompt_skill_refs "$file")

  if [[ "${#refs[@]}" -eq 0 ]]; then
    if [[ "$MODE" == "strict" ]]; then
      record_error "Prompt must reference at least one skill: ${file}"
    else
      record_warn "Prompt does not reference a skill path: ${file}"
    fi
    return
  fi

  for ref in "${refs[@]}"; do
    if [[ ! -f "${base_dir}/${ref}" ]]; then
      if [[ "$MODE" == "strict" ]]; then
        record_error "Prompt references missing skill path '${ref}' in ${file}"
      else
        record_warn "Prompt references missing skill path '${ref}' in ${file}"
      fi
    fi
  done
}

validate_instruction_file() {
  local file="$1"

  check_required_keys "$file" error applyTo
  if ! grep -Eq '^# ' "$file"; then
    record_error "Instruction missing top heading: ${file}"
  fi
}

validate_skill_file() {
  local file="$1"
  local section_severity="error"

  [[ "$MODE" == "legacy-compatible" ]] && section_severity="warn"

  check_required_keys "$file" error name description

  if ! has_heading_regex "$file" '^## When to [Uu]se$'; then
    record_issue "$section_severity" "Skill missing '## When to use' section: ${file}"
  fi

  if ! has_heading_regex "$file" '^## (Validation|Checklist|Testing|Test stack)$'; then
    if [[ "$MODE" == "strict" ]]; then
      record_error "Skill missing validation/testing section: ${file}"
    else
      record_warn "Skill missing validation/testing section: ${file}"
    fi
  fi
}

validate_agents_dir() {
  local agents_dir="$1"
  local file
  local count=0

  if [[ ! -d "$agents_dir" ]]; then
    record_warn "No .github/agents directory found in ${agents_dir%/.github/agents}"
    return
  fi

  while IFS= read -r file; do
    count=$((count + 1))
    check_required_keys "$file" error name description tools

    if ! grep -Eq '^# ' "$file"; then
      record_error "Agent missing top heading: ${file}"
    fi
    if ! has_heading_exact "$file" '## Objective'; then
      record_error "Agent missing '## Objective' section: ${file}"
    fi
    if ! has_heading_exact "$file" '## Restrictions'; then
      record_error "Agent missing '## Restrictions' section: ${file}"
    fi
  done < <(find "$agents_dir" -type f -name '*.agent.md' | sort)

  if [[ "$count" -eq 0 ]]; then
    record_warn "No custom agents found under ${agents_dir}"
  fi
}

validate_skill_dirs() {
  local skills_dir="$1"
  local dir

  if [[ ! -d "$skills_dir" ]]; then
    record_warn "No .github/skills directory found in ${skills_dir%/.github/skills}"
    return
  fi

  while IFS= read -r dir; do
    if [[ ! -f "${dir}/SKILL.md" ]]; then
      if [[ "$MODE" == "strict" ]]; then
        record_error "Skill directory missing SKILL.md: ${dir}"
      else
        record_warn "Skill directory missing SKILL.md: ${dir}"
      fi
    fi
  done < <(find "$skills_dir" -mindepth 1 -maxdepth 1 -type d | sort)

  return 0
}

validate_unreferenced_skills() {
  local prompts_dir="$1"
  local skills_dir="$2"
  local skill
  local skill_ref

  if [[ ! -d "$prompts_dir" || ! -d "$skills_dir" ]]; then
    return 0
  fi

  while IFS= read -r skill; do
    skill_ref="${skill#"${ROOT_DIR}"/}"
    if ! grep -R -q "$skill_ref" "$prompts_dir"; then
      record_warn "Unreferenced skill (consider using in prompts): ${skill_ref}"
    fi
  done < <(find "$skills_dir" -type f -name 'SKILL.md' | sort)

  return 0
}

validate_workflow_pinning() {
  local workflows_dir="$1"
  local file
  local token
  local ref
  local severity="error"

  [[ "$MODE" == "legacy-compatible" ]] && severity="warn"

  if [[ ! -d "$workflows_dir" ]]; then
    record_warn "No .github/workflows directory found in ${workflows_dir%/.github/workflows}"
    return
  fi

  while IFS= read -r file; do
    while IFS= read -r token; do
      [[ -n "$token" ]] || continue

      if [[ "$token" == ./* || "$token" == docker://* ]]; then
        continue
      fi

      if [[ "$token" != *"@"* ]]; then
        record_issue "$severity" "Workflow action reference is not pinned by SHA: ${file} -> ${token}"
        continue
      fi

      ref="${token##*@}"
      if [[ ! "$ref" =~ ^[a-f0-9]{40}$ ]]; then
        record_issue "$severity" "Workflow action reference is not full SHA: ${file} -> ${token}"
      fi
    done < <(grep -oE 'uses:[[:space:]]*[^[:space:]]+' "$file" | sed -E 's/^uses:[[:space:]]*//' || true)
  done < <(find "$workflows_dir" -type f \( -name '*.yml' -o -name '*.yaml' \) | sort)

  return 0
}

validate_target() {
  local target_root="$1"
  local label="$2"
  local github_dir="${target_root}/.github"
  local prompts_dir="${github_dir}/prompts"
  local instructions_dir="${github_dir}/instructions"
  local skills_dir="${github_dir}/skills"
  local agents_dir="${github_dir}/agents"
  local workflows_dir="${github_dir}/workflows"
  local file

  if [[ ! -d "$github_dir" ]]; then
    if [[ "$MODE" == "strict" ]]; then
      record_error "${label}: missing .github directory"
    else
      record_warn "${label}: missing .github directory"
    fi
    return
  fi

  log_info "🔎 Validating ${label} (.github)"

  if [[ -d "$prompts_dir" ]]; then
    while IFS= read -r file; do
      validate_prompt_file "$file" "$target_root"
    done < <(find "$prompts_dir" -type f -name '*.prompt.md' | sort)
  else
    record_warn "${label}: no .github/prompts directory"
  fi

  if [[ -d "$instructions_dir" ]]; then
    while IFS= read -r file; do
      validate_instruction_file "$file"
    done < <(find "$instructions_dir" -type f -name '*.instructions.md' | sort)
  else
    record_warn "${label}: no .github/instructions directory"
  fi

  validate_skill_dirs "$skills_dir"
  if [[ -d "$skills_dir" ]]; then
    while IFS= read -r file; do
      validate_skill_file "$file"
    done < <(find "$skills_dir" -type f -name 'SKILL.md' | sort)
  fi

  validate_agents_dir "$agents_dir"
  validate_unreferenced_skills "$prompts_dir" "$skills_dir"
  validate_workflow_pinning "$workflows_dir"

  return 0
}

main() {
  local target
  local repo_name
  local repo_path
  local targets=()

  parse_args "$@"

  log_info "🚀 Starting Copilot customization validation (scope=${SCOPE}, mode=${MODE})"

  case "$SCOPE" in
    root)
      targets+=("$ROOT_DIR")
      ;;
    all)
      targets+=("$ROOT_DIR")
      for target in "$ROOT_DIR"/*; do
        [[ -d "$target" ]] || continue
        [[ -d "$target/.github" ]] || continue
        targets+=("$target")
      done
      ;;
    repo=*)
      targets+=("$ROOT_DIR")
      repo_name="${SCOPE#repo=}"
      repo_path="$ROOT_DIR/$repo_name"
      if [[ ! -d "$repo_path" ]]; then
        record_error "Requested repo does not exist: ${repo_name}"
        exit 1
      fi
      targets+=("$repo_path")
      ;;
  esac

  for target in "${targets[@]}"; do
    if [[ "$target" == "$ROOT_DIR" ]]; then
      validate_target "$target" "root"
    else
      validate_target "$target" "$(basename "$target")"
    fi
  done

  if [[ "$FAILURES" -gt 0 ]]; then
    log_error "Validation failed with ${FAILURES} error(s) and ${WARNINGS} warning(s)."
    write_json_report "failed"
    return 1
  fi

  if [[ "$WARNINGS" -gt 0 ]]; then
    log_warn "Validation passed with ${WARNINGS} warning(s)."
    write_json_report "passed-with-warnings"
    log_success "🏁 Copilot customization validation passed."
    return 0
  fi

  write_json_report "passed"
  log_success "🏁 Copilot customization validation passed."
  return 0
}

main "$@"
