#!/usr/bin/env bash
#
# Purpose: Validate Copilot customization files in root layout or .github layout.
# Usage examples:
#   ./scripts/validate-copilot-customizations.sh
#   ./scripts/validate-copilot-customizations.sh --scope root --mode strict
#   ./.github/scripts/validate-copilot-customizations.sh --scope all --mode legacy-compatible
#   ./.github/scripts/validate-copilot-customizations.sh --scope repo=my-repo --mode legacy-compatible
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$(basename "$(cd "${SCRIPT_DIR}/.." && pwd)")" == ".github" ]]; then
  ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
else
  ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi
readonly ROOT_DIR

MODE="strict"
SCOPE="root"
REPORT_FORMAT="text"
REPORT_FILE=""

FAILURES=0
WARNINGS=0
FINDINGS=()

log_info() { echo "ℹ️  $*"; }
log_warn() { echo "⚠️  $*"; }
log_error() { echo "❌ $*" >&2; }
log_success() { echo "✅ $*"; }

usage() {
  cat << 'USAGE'
Usage: validate-copilot-customizations.sh [--scope root|all|repo=<name>] [--mode strict|legacy-compatible] [--report text|json] [--report-file <path>]

Options:
  --scope   Validation scope (default: root)
            root            Validate only workspace root Copilot config
            all             Validate root + all immediate sub-repos that contain Copilot config
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
  FINDINGS+=("error|$msg")
}

record_warn() {
  local msg="$1"
  log_warn "$msg"
  WARNINGS=$((WARNINGS + 1))
  FINDINGS+=("warning|$msg")
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
  local findings_json
  local entry
  local severity
  local message
  local is_first=true
  local finding_count=0

  [[ "$REPORT_FORMAT" == "json" ]] || return 0

  timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

  findings_json="["
  for entry in "${FINDINGS[@]-}"; do
    [[ -n "${entry:-}" ]] || continue
    finding_count=$((finding_count + 1))
    severity="${entry%%|*}"
    message="${entry#*|}"
    if [[ "$is_first" == true ]]; then
      is_first=false
    else
      findings_json+=","
    fi
    findings_json+=$'\n    {"severity":"'
    findings_json+="$(json_escape "$severity")"
    findings_json+='","message":"'
    findings_json+="$(json_escape "$message")"
    findings_json+='"}'
  done
  if [[ "$finding_count" -gt 0 ]]; then
    findings_json+=$'\n  ]'
  else
    findings_json+="]"
  fi

  payload="$(cat <<EOF
{
  "status": "$(json_escape "$status")",
  "mode": "$(json_escape "$MODE")",
  "scope": "$(json_escape "$SCOPE")",
  "failures": ${FAILURES},
  "warnings": ${WARNINGS},
  "findings": ${findings_json},
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
  frontmatter "$file" | grep -Eq "^${key}:[[:space:]]*.*$"
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

frontmatter_value() {
  local file="$1"
  local key="$2"
  frontmatter "$file" | awk -v wanted="$key" '
    {
      line = $0
      sub(/^[[:space:]]+/, "", line)
      if (line ~ ("^" wanted ":[[:space:]]*")) {
        sub("^" wanted ":[[:space:]]*", "", line)
        print line
        exit
      }
    }
  '
}

validate_frontmatter_structure() {
  local file="$1"
  local severity="$2"

  if [[ "$(head -n 1 "$file" 2>/dev/null)" != "---" ]]; then
    record_issue "$severity" "File is missing opening frontmatter fence: ${file}"
    return 1
  fi

  if [[ "$(grep -c '^---$' "$file")" -lt 2 ]]; then
    record_issue "$severity" "File has malformed frontmatter fence: ${file}"
    return 1
  fi

  return 0
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

prompt_expected_name() {
  local file="$1"
  local name

  name="$(basename "$file")"

  case "$name" in
    tech-ai-github-action.prompt.md)
      printf '%s' "TechAIGitHubAction"
      ;;
    tech-ai-github-composite-action.prompt.md)
      printf '%s' "TechAICompositeAction"
      ;;
    tech-ai-github-pr-description.prompt.md)
      printf '%s' "TechAIPRDescription"
      ;;
    tech-ai-add-platform.prompt.md)
      printf '%s' "TechAIAddPlatform"
      ;;
    tech-ai-add-report-script.prompt.md)
      printf '%s' "TechAIAddReportScript"
      ;;
    tech-ai-cicd-workflow.prompt.md)
      printf '%s' "TechAICICDWorkflow"
      ;;
    tech-ai-terraform-module.prompt.md)
      printf '%s' "TechAITerraformModule"
      ;;
    tech-ai-*.prompt.md)
      tech_ai_prompt_name "${name%.prompt.md}"
      ;;
    *.prompt.md)
      printf '%s' "${name%.prompt.md}"
      ;;
    *)
      return 1
      ;;
  esac
}

tech_ai_prompt_name() {
  local stem="$1"
  local remainder
  local output="TechAI"
  local part
  local first_char

  remainder="${stem#tech-ai-}"
  IFS='-' read -r -a parts <<< "$remainder"
  for part in "${parts[@]}"; do
    [[ -n "$part" ]] || continue
    first_char="$(printf '%s' "${part:0:1}" | tr '[:lower:]' '[:upper:]')"
    output+="${first_char}${part:1}"
  done

  printf '%s' "$output"
}

internal_asset_identifier() {
  local file="$1"
  local base
  local parent

  case "$file" in
    *.prompt.md)
      base="$(basename "$file")"
      printf '%s' "${base%.prompt.md}"
      ;;
    *.agent.md)
      base="$(basename "$file")"
      printf '%s' "${base%.agent.md}"
      ;;
    */SKILL.md)
      parent="$(basename "$(dirname "$file")")"
      printf '%s' "$parent"
      ;;
    *)
      return 1
      ;;
  esac
}

validate_repo_local_prompt_naming() {
  local file="$1"
  local severity="error"
  local actual_name=""
  local expected_internal_name=""

  [[ "$MODE" == "legacy-compatible" ]] && severity="warn"

  actual_name="$(frontmatter_value "$file" "name")"
  expected_internal_name="$(internal_asset_identifier "$file" || true)"

  case "$(basename "$file")" in
    tech-ai-*.prompt.md)
      return 0
      ;;
    internal-*.prompt.md)
      if [[ -n "$actual_name" && "$actual_name" != internal-* ]]; then
        record_issue "$severity" "Repository-internal prompt name must start with 'internal-': ${file}"
      fi
      if [[ -n "$actual_name" && -n "$expected_internal_name" && "$actual_name" != "$expected_internal_name" ]]; then
        record_issue "$severity" "Repository-internal prompt name must match filename stem '${expected_internal_name}': ${file}"
      fi
      return 0
      ;;
    *)
      record_issue "$severity" "Repository-internal prompt filename must start with 'internal-': ${file}"
      if [[ -n "$actual_name" && "$actual_name" != internal-* ]]; then
        record_issue "$severity" "Repository-internal prompt name must start with 'internal-': ${file}"
      fi
      ;;
  esac
}

validate_repo_local_skill_naming() {
  local file="$1"
  local severity="error"
  local actual_name=""
  local expected_internal_name=""
  local skill_dir

  [[ "$MODE" == "legacy-compatible" ]] && severity="warn"

  actual_name="$(frontmatter_value "$file" "name")"
  expected_internal_name="$(internal_asset_identifier "$file" || true)"
  skill_dir="$(basename "$(dirname "$file")")"

  case "$skill_dir" in
    tech-ai-*)
      return 0
      ;;
    internal-*)
      if [[ -n "$actual_name" && "$actual_name" != internal-* ]]; then
        record_issue "$severity" "Repository-internal skill name must start with 'internal-': ${file}"
      fi
      if [[ -n "$actual_name" && -n "$expected_internal_name" && "$actual_name" != "$expected_internal_name" ]]; then
        record_issue "$severity" "Repository-internal skill name must match directory name '${expected_internal_name}': ${file}"
      fi
      return 0
      ;;
    *)
      record_issue "$severity" "Repository-internal skill directory must start with 'internal-': ${file}"
      if [[ -n "$actual_name" && "$actual_name" != internal-* ]]; then
        record_issue "$severity" "Repository-internal skill name must start with 'internal-': ${file}"
      fi
      ;;
  esac
}

validate_repo_local_agent_naming() {
  local file="$1"
  local severity="error"
  local actual_name=""
  local expected_internal_name=""

  [[ "$MODE" == "legacy-compatible" ]] && severity="warn"

  actual_name="$(frontmatter_value "$file" "name")"
  expected_internal_name="$(internal_asset_identifier "$file" || true)"

  case "$(basename "$file")" in
    tech-ai-*.agent.md)
      return 0
      ;;
    internal-*.agent.md)
      if [[ -n "$actual_name" && "$actual_name" != internal-* ]]; then
        record_issue "$severity" "Repository-internal agent name must start with 'internal-': ${file}"
      fi
      if [[ -n "$actual_name" && -n "$expected_internal_name" && "$actual_name" != "$expected_internal_name" ]]; then
        record_issue "$severity" "Repository-internal agent name must match filename stem '${expected_internal_name}': ${file}"
      fi
      return 0
      ;;
    *)
      record_issue "$severity" "Repository-internal agent filename must start with 'internal-': ${file}"
      if [[ -n "$actual_name" && "$actual_name" != internal-* ]]; then
        record_issue "$severity" "Repository-internal agent name must start with 'internal-': ${file}"
      fi
      ;;
  esac
}

validate_prompt_name_policy() {
  local file="$1"
  local expected_name
  local actual_name
  local severity="error"

  [[ "$MODE" == "legacy-compatible" ]] && severity="warn"

  if ! expected_name="$(prompt_expected_name "$file")"; then
    return 0
  fi

  actual_name="$(frontmatter_value "$file" "name")"
  [[ -n "$actual_name" ]] || return 0

  if [[ "$actual_name" != "$expected_name" ]]; then
    record_issue "$severity" "Prompt name policy mismatch in ${file}: expected '${expected_name}', found '${actual_name}'"
  fi
}

prompt_skill_refs() {
  local file="$1"
  grep -oE '(\.github/)?skills/[A-Za-z0-9._/-]+/SKILL\.md' "$file" | sort -u || true
}

strip_github_prefix() {
  local value="$1"
  if [[ "$value" == .github/* ]]; then
    printf '%s' "${value#".github/"}"
    return 0
  fi

  printf '%s' "$value"
}

resolve_reference_file() {
  local target_root="$1"
  local config_dir="$2"
  local ref="$3"
  local ref_no_prefix

  ref_no_prefix="$(strip_github_prefix "$ref")"

  if [[ -f "${target_root}/${ref}" ]]; then
    printf '%s' "${target_root}/${ref}"
    return 0
  fi

  if [[ -f "${target_root}/${ref_no_prefix}" ]]; then
    printf '%s' "${target_root}/${ref_no_prefix}"
    return 0
  fi

  if [[ -f "${config_dir}/${ref}" ]]; then
    printf '%s' "${config_dir}/${ref}"
    return 0
  fi

  if [[ -f "${config_dir}/${ref_no_prefix}" ]]; then
    printf '%s' "${config_dir}/${ref_no_prefix}"
    return 0
  fi

  return 1
}

resolve_config_dir() {
  local target_root="$1"

  if [[ -f "${target_root}/copilot-instructions.md" && -d "${target_root}/instructions" ]]; then
    printf '%s' "${target_root}"
    return 0
  fi

  if [[ -d "${target_root}/.github" ]]; then
    printf '%s' "${target_root}/.github"
    return 0
  fi

  return 1
}

has_copilot_config() {
  local target_root="$1"

  if resolve_config_dir "$target_root" >/dev/null; then
    return 0
  fi

  return 1
}

validate_prompt_file() {
  local file="$1"
  local target_root="$2"
  local config_dir="$3"
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

  validate_frontmatter_structure "$file" error || true

  if frontmatter "$file" | grep -Eq '^mode:[[:space:]]*'; then
    severity="error"
    [[ "$MODE" == "legacy-compatible" ]] && severity="warn"
    record_issue "$severity" "Legacy prompt key 'mode' found: ${file}"
  fi

  validate_prompt_name_policy "$file"
  validate_repo_local_prompt_naming "$file"

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
    if ! resolve_reference_file "$target_root" "$config_dir" "$ref" >/dev/null; then
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

  validate_frontmatter_structure "$file" error || true

  if [[ "$MODE" == "strict" ]]; then
    check_required_keys "$file" error applyTo description
  else
    check_required_keys "$file" error applyTo
    check_optional_keys "$file" description
  fi

  if ! grep -Eq '^# ' "$file"; then
    record_error "Instruction missing top heading: ${file}"
  fi
}

validate_skill_file() {
  local file="$1"
  local section_severity="error"

  [[ "$MODE" == "legacy-compatible" ]] && section_severity="warn"

  validate_frontmatter_structure "$file" error || true
  check_required_keys "$file" error name description
  validate_repo_local_skill_naming "$file"

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
  local semantic_severity="error"

  [[ "$MODE" == "legacy-compatible" ]] && semantic_severity="warn"

  if [[ ! -d "$agents_dir" ]]; then
    record_warn "No .github/agents directory found in ${agents_dir%/.github/agents}"
    return
  fi

  while IFS= read -r file; do
    count=$((count + 1))
    validate_frontmatter_structure "$file" error || true
    check_required_keys "$file" error name description tools
    validate_repo_local_agent_naming "$file"

    if ! grep -Eq '^# ' "$file"; then
      record_error "Agent missing top heading: ${file}"
    fi
    if ! has_heading_exact "$file" '## Objective'; then
      record_error "Agent missing '## Objective' section: ${file}"
    fi
    if ! has_heading_exact "$file" '## Restrictions'; then
      record_error "Agent missing '## Restrictions' section: ${file}"
    fi

    case "$(basename "$file")" in
      tech-ai-planner.agent.md)
        if ! has_heading_exact "$file" '## Scope guard'; then
          record_issue "$semantic_severity" "Planner agent missing '## Scope guard' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Skill and prompt awareness'; then
          record_issue "$semantic_severity" "Planner agent missing '## Skill and prompt awareness' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Handoff output'; then
          record_issue "$semantic_severity" "Planner agent missing '## Handoff output' section: ${file}"
        fi
        if ! grep -Fq 'security-baseline.md' "$file"; then
          record_issue "$semantic_severity" "Planner agent should reference security baseline: ${file}"
        fi
        ;;
      tech-ai-implementer.agent.md)
        if ! has_heading_exact "$file" '## Handoff input'; then
          record_issue "$semantic_severity" "Implementer agent missing '## Handoff input' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Stack resolution'; then
          record_issue "$semantic_severity" "Implementer agent missing '## Stack resolution' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Commit messages'; then
          record_issue "$semantic_severity" "Implementer agent missing '## Commit messages' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Execution policy'; then
          record_issue "$semantic_severity" "Implementer agent missing '## Execution policy' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Error recovery'; then
          record_issue "$semantic_severity" "Implementer agent missing '## Error recovery' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Handoff output'; then
          record_issue "$semantic_severity" "Implementer agent missing '## Handoff output' section: ${file}"
        fi
        if ! grep -Fq 'security-baseline.md' "$file"; then
          record_issue "$semantic_severity" "Implementer agent should reference security baseline: ${file}"
        fi
        if ! grep -Fq 'copilot-commit-message-instructions.md' "$file"; then
          record_issue "$semantic_severity" "Implementer agent should reference commit message instructions: ${file}"
        fi
        if ! grep -Fq 'scripts/validate-copilot-customizations.sh' "$file"; then
          record_issue "$semantic_severity" "Implementer agent should reference customization validator: ${file}"
        fi
        ;;
      tech-ai-reviewer.agent.md)
        if ! has_heading_exact "$file" '## Review format'; then
          record_issue "$semantic_severity" "Reviewer agent missing '## Review format' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Diff-first approach'; then
          record_issue "$semantic_severity" "Reviewer agent missing '## Diff-first approach' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Specialist delegation'; then
          record_issue "$semantic_severity" "Reviewer agent missing '## Specialist delegation' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Handoff output'; then
          record_issue "$semantic_severity" "Reviewer agent missing '## Handoff output' section: ${file}"
        fi
        if ! grep -Fq 'security-baseline.md' "$file"; then
          record_issue "$semantic_severity" "Reviewer agent should reference security baseline: ${file}"
        fi
        if ! grep -Fq 'copilot-code-review-instructions.md' "$file"; then
          record_issue "$semantic_severity" "Reviewer agent should reference code review instructions: ${file}"
        fi
        ;;
      tech-ai-global-customization-builder.agent.md)
        if ! has_heading_exact "$file" '## Source of truth'; then
          record_issue "$semantic_severity" "Global customization builder missing '## Source of truth' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Creation protocol'; then
          record_issue "$semantic_severity" "Global customization builder missing '## Creation protocol' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Token discipline'; then
          record_issue "$semantic_severity" "Global customization builder missing '## Token discipline' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Validation'; then
          record_issue "$semantic_severity" "Global customization builder missing '## Validation' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Handoff'; then
          record_issue "$semantic_severity" "Global customization builder missing '## Handoff' section: ${file}"
        fi
        if ! grep -Fq 'AGENTS.md' "$file"; then
          record_issue "$semantic_severity" "Global customization builder should reference root AGENTS.md: ${file}"
        fi
        if ! grep -Fq 'security-baseline.md' "$file"; then
          record_issue "$semantic_severity" "Global customization builder should reference security baseline: ${file}"
        fi
        if ! grep -Fq 'DEPRECATION.md' "$file"; then
          record_issue "$semantic_severity" "Global customization builder should reference deprecation policy: ${file}"
        fi
        if ! grep -Fq 'scripts/validate-copilot-customizations.sh' "$file"; then
          record_issue "$semantic_severity" "Global customization builder should reference customization validator: ${file}"
        fi
        if ! grep -Fq 'TechAIGlobalCustomizationAuditor' "$file"; then
          record_issue "$semantic_severity" "Global customization builder should hand off to TechAIGlobalCustomizationAuditor: ${file}"
        fi
        ;;
      tech-ai-global-customization-auditor.agent.md)
        if ! has_heading_exact "$file" '## Audit protocol'; then
          record_issue "$semantic_severity" "Global customization auditor missing '## Audit protocol' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Severity output'; then
          record_issue "$semantic_severity" "Global customization auditor missing '## Severity output' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Validation'; then
          record_issue "$semantic_severity" "Global customization auditor missing '## Validation' section: ${file}"
        fi
        if ! has_heading_exact "$file" '## Handoff'; then
          record_issue "$semantic_severity" "Global customization auditor missing '## Handoff' section: ${file}"
        fi
        if ! grep -Fq 'scripts/validate-copilot-customizations.sh' "$file"; then
          record_issue "$semantic_severity" "Global customization auditor should reference customization validator: ${file}"
        fi
        if ! grep -Fq 'TechAIGlobalCustomizationBuilder' "$file"; then
          record_issue "$semantic_severity" "Global customization auditor should route major findings to TechAIGlobalCustomizationBuilder: ${file}"
        fi
        ;;
    esac
  done < <(find "$agents_dir" -type f -name '*.agent.md' | sort)

  if [[ "$count" -eq 0 ]]; then
    record_warn "No custom agents found under ${agents_dir}"
  fi
}

resolve_agents_file() {
  local target_root="$1"
  local config_dir="$2"

  if [[ -f "${target_root}/AGENTS.md" ]]; then
    printf '%s' "${target_root}/AGENTS.md"
    return 0
  fi

  if [[ -f "${config_dir}/AGENTS.md" ]]; then
    printf '%s' "${config_dir}/AGENTS.md"
    return 0
  fi

  return 1
}

agents_contains_path() {
  local agents_file="$1"
  local path="$2"
  local alternate_path

  alternate_path="$path"
  if [[ "$path" == .github/* ]]; then
    alternate_path="${path#.github/}"
  else
    alternate_path=".github/${path}"
  fi

  if grep -Fq "$path" "$agents_file" || grep -Fq "$alternate_path" "$agents_file"; then
    return 0
  fi

  return 1
}

validate_agents_inventory() {
  local target_root="$1"
  local config_dir="$2"
  local instructions_dir="$3"
  local prompts_dir="$4"
  local skills_dir="$5"
  local agents_file=""
  local root_agents_file="${target_root}/AGENTS.md"
  local legacy_agents_file="${config_dir}/AGENTS.md"
  local file
  local rel_path
  local severity="error"

  [[ "$MODE" == "legacy-compatible" ]] && severity="warn"

  if [[ -f "$root_agents_file" ]]; then
    agents_file="$root_agents_file"
  elif [[ -f "$legacy_agents_file" ]]; then
    record_issue "$severity" "AGENTS.md must live in repository root; found legacy ${legacy_agents_file}"
    agents_file="$legacy_agents_file"
  else
    record_issue "$severity" "Missing AGENTS.md in repository root: ${root_agents_file}"
    return 0
  fi

  if [[ -d "$instructions_dir" ]]; then
    while IFS= read -r file; do
      rel_path="${file#"${target_root}/"}"
      if ! agents_contains_path "$agents_file" "$rel_path"; then
        record_issue "$severity" "AGENTS.md is missing instruction inventory entry for '${rel_path}'"
      fi
    done < <(find "$instructions_dir" -type f -name '*.instructions.md' | sort)
  fi

  if [[ -d "$prompts_dir" ]]; then
    while IFS= read -r file; do
      rel_path="${file#"${target_root}/"}"
      if ! agents_contains_path "$agents_file" "$rel_path"; then
        record_issue "$severity" "AGENTS.md is missing prompt inventory entry for '${rel_path}'"
      fi
    done < <(find "$prompts_dir" -type f -name '*.prompt.md' | sort)
  fi

  if [[ -d "$skills_dir" ]]; then
    while IFS= read -r file; do
      rel_path="${file#"${target_root}/"}"
      if ! agents_contains_path "$agents_file" "$rel_path"; then
        record_issue "$severity" "AGENTS.md is missing skill inventory entry for '${rel_path}'"
      fi
    done < <(find "$skills_dir" -type f -name 'SKILL.md' | sort)
  fi

  return 0
}

validate_codeowners_placeholder() {
  local target_root="$1"
  local config_dir="$2"
  local codeowners_file
  local checked_files=""

  for codeowners_file in "${target_root}/CODEOWNERS" "${config_dir}/CODEOWNERS"; do
    [[ -f "$codeowners_file" ]] || continue

    if [[ "$checked_files" == *"|${codeowners_file}|"* ]]; then
      continue
    fi
    checked_files="${checked_files}|${codeowners_file}|"

    if grep -Fq '@your-org/platform-governance-team' "$codeowners_file"; then
      record_warn "CODEOWNERS still uses template placeholder owner in ${codeowners_file}"
    fi
  done

  return 0
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
  local prefixed_skill_ref

  if [[ ! -d "$prompts_dir" || ! -d "$skills_dir" ]]; then
    return 0
  fi

  while IFS= read -r skill; do
    skill_ref="skills/${skill#"${skills_dir}/"}"
    prefixed_skill_ref=".github/${skill_ref}"

    if ! grep -R -q "$skill_ref" "$prompts_dir" && ! grep -R -q "$prefixed_skill_ref" "$prompts_dir"; then
      record_warn "Unreferenced skill (consider using in prompts): ${skill_ref}"
    fi
  done < <(find "$skills_dir" -type f -name 'SKILL.md' | sort)

  return 0
}

validate_workflow_pinning() {
  local workflows_dir="$1"
  local file
  local entry
  local line_number
  local line_text
  local token
  local ref
  local severity="error"

  [[ "$MODE" == "legacy-compatible" ]] && severity="warn"

  if [[ ! -d "$workflows_dir" ]]; then
    record_warn "No .github/workflows directory found in ${workflows_dir%/.github/workflows}"
    return
  fi

  while IFS= read -r file; do
    while IFS= read -r entry; do
      [[ -n "$entry" ]] || continue

      line_number="${entry%%:*}"
      line_text="${entry#*:}"
      token="$(printf '%s\n' "$line_text" | sed -E 's/.*uses:[[:space:]]*([^[:space:]]+).*/\1/')"
      [[ -n "$token" ]] || continue

      if [[ "$token" == ./* || "$token" == .github/actions/* || "$token" == docker://* ]]; then
        continue
      fi

      if [[ "$token" != *"@"* ]]; then
        record_issue "$severity" "Workflow action reference is not pinned by SHA: ${file}:${line_number} -> ${token}"
        continue
      fi

      ref="${token##*@}"
      if [[ ! "$ref" =~ ^[a-f0-9]{40}$ ]]; then
        record_issue "$severity" "Workflow action reference is not full SHA: ${file}:${line_number} -> ${token}"
        continue
      fi

      if ! printf '%s\n' "$line_text" | grep -Eq '#[[:space:]]*[^#]*https://github\.com/[^[:space:]]+/[^[:space:]]+/releases/tag/[^[:space:]]+'; then
        record_issue "$severity" "Workflow SHA pin is missing adjacent release URL comment: ${file}:${line_number} -> ${token}"
      fi
    done < <(grep -nE 'uses:[[:space:]]*[^[:space:]]+' "$file" || true)
  done < <(find "$workflows_dir" -type f \( -name '*.yml' -o -name '*.yaml' \) | sort)

  return 0
}

validate_workflow_permissions() {
  local workflows_dir="$1"
  local file
  local severity="error"

  [[ "$MODE" == "legacy-compatible" ]] && severity="warn"

  if [[ ! -d "$workflows_dir" ]]; then
    return
  fi

  while IFS= read -r file; do
    if ! grep -Eq '^[[:space:]]*permissions:[[:space:]]*' "$file"; then
      record_issue "$severity" "Workflow missing permissions block: ${file}"
    fi
  done < <(find "$workflows_dir" -mindepth 1 -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) | sort)

  return 0
}

validate_pr_template_consistency() {
  local github_dir="$1"
  local lower_template="${github_dir}/pull_request_template.md"
  local upper_template="${github_dir}/PULL_REQUEST_TEMPLATE.md"
  local severity="error"

  [[ "$MODE" == "legacy-compatible" ]] && severity="warn"

  if [[ ! -f "$lower_template" && ! -f "$upper_template" ]]; then
    record_issue "$severity" "Missing PR template in ${github_dir} (expected pull_request_template.md or PULL_REQUEST_TEMPLATE.md)"
    return 0
  fi

  if [[ -f "$lower_template" && -f "$upper_template" ]] && ! cmp -s "$lower_template" "$upper_template"; then
    record_issue "$severity" "PR template files diverge in ${github_dir}: pull_request_template.md vs PULL_REQUEST_TEMPLATE.md"
  fi

  return 0
}

validate_target() {
  local target_root="$1"
  local label="$2"
  local github_dir=""
  local prompts_dir="${github_dir}/prompts"
  local instructions_dir="${github_dir}/instructions"
  local skills_dir="${github_dir}/skills"
  local agents_dir="${github_dir}/agents"
  local workflows_dir="${github_dir}/workflows"
  local file

  if ! github_dir="$(resolve_config_dir "$target_root")"; then
    if [[ "$MODE" == "strict" ]]; then
      record_error "${label}: missing Copilot configuration root"
    else
      record_warn "${label}: missing Copilot configuration root"
    fi
    return
  fi

  prompts_dir="${github_dir}/prompts"
  instructions_dir="${github_dir}/instructions"
  skills_dir="${github_dir}/skills"
  agents_dir="${github_dir}/agents"
  workflows_dir="${github_dir}/workflows"

  log_info "🔎 Validating ${label} (${github_dir})"

  if [[ -d "$prompts_dir" ]]; then
    while IFS= read -r file; do
      validate_prompt_file "$file" "$target_root" "$github_dir"
    done < <(find "$prompts_dir" -type f -name '*.prompt.md' | sort)
  else
    record_warn "${label}: no prompts directory"
  fi

  if [[ -d "$instructions_dir" ]]; then
    while IFS= read -r file; do
      validate_instruction_file "$file"
    done < <(find "$instructions_dir" -type f -name '*.instructions.md' | sort)
  else
    record_warn "${label}: no instructions directory"
  fi

  validate_skill_dirs "$skills_dir"
  if [[ -d "$skills_dir" ]]; then
    while IFS= read -r file; do
      validate_skill_file "$file"
    done < <(find "$skills_dir" -type f -name 'SKILL.md' | sort)
  fi

  validate_agents_dir "$agents_dir"
  validate_agents_inventory "$target_root" "$github_dir" "$instructions_dir" "$prompts_dir" "$skills_dir"
  validate_codeowners_placeholder "$target_root" "$github_dir"
  validate_unreferenced_skills "$prompts_dir" "$skills_dir"
  validate_workflow_pinning "$workflows_dir"
  validate_workflow_permissions "$workflows_dir"
  validate_pr_template_consistency "$github_dir"

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
        has_copilot_config "$target" || continue
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
