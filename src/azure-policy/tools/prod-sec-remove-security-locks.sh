#!/usr/bin/env bash
# Temporarily remove direct locks from the four PROD-SEC resources listed below.
# Target subscription: PROD-SEC (0da48c97-355f-4050-a520-f11a18b8be90).
# Prerequisites: Bash 3.2+, Azure CLI, jq, an authenticated session (az login),
# and Microsoft.Authorization/locks/read and /delete permissions on the targets.
#
# Run from the repository root:
#   ./src/azure-policy/tools/prod-sec-remove-security-locks.sh            # Plan, then yes/no
#   ./src/azure-policy/tools/prod-sec-remove-security-locks.sh --dry-run  # Preview only
#   ./src/azure-policy/tools/prod-sec-remove-security-locks.sh --help     # All options
#
# After the plan, answer yes to apply or no to cancel. Only the exact answer yes
# authorizes deletion; Enter, EOF and any other answer cancel without changes.
# --dry-run never prompts or deletes. --apply also requires yes/no confirmation.
# Errors are collected while other locks continue; the final report verifies
# all planned locks and lists request errors separately from verified state.
# Exit codes: 0 = completed (possibly with request warnings);
#             1 = failure or remaining/new/inherited locks;
#             2 = invalid arguments; 3 = confirmation cancelled.
#             130/143 = interrupted; verify current state before retrying.
#
# Resource group/subscription locks, policies and RBAC assignments are not changed.
# Active policies may recreate locks. Restore protection after maintenance.
# Rerun the preview before retrying; --no-color disables terminal colors.

set -euo pipefail

SUBSCRIPTION_NAME='PROD-SEC'
SUBSCRIPTION='0da48c97-355f-4050-a520-f11a18b8be90'
RESOURCES=(
  "/subscriptions/$SUBSCRIPTION/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogs"
  "/subscriptions/$SUBSCRIPTION/resourceGroups/sec-p-rg-nit/providers/Microsoft.Storage/storageAccounts/ppseclogsitn"
  "/subscriptions/$SUBSCRIPTION/resourceGroups/sec-p-rg-neu/providers/Microsoft.Storage/storageAccounts/ppseclogsneu"
  "/subscriptions/$SUBSCRIPTION/resourceGroups/sec-p-sentinel/providers/Microsoft.OperationalInsights/workspaces/sec-p-law"
)
WORK_DIR=''
ACCENT=''
RESET=''

usage() {
  printf '%s\n' \
    '🔐 PROD-SEC | Security resource lock removal (Bash 3.2+, Azure CLI, jq)' \
    '' \
    'Usage: ./prod-sec-remove-security-locks.sh [--dry-run | --apply] [--no-color]' \
    '' \
    'Default: show the plan, then ask Apply? [yes/no]. Only yes deletes locks.' \
    '--dry-run: preview only, without prompting or changing Azure.' \
    '--apply: explicitly select the same plan and yes/no confirmation flow.' \
    '--no-color: disable terminal colors; NO_COLOR is also supported.' \
    '' \
    "Fixed subscription: $SUBSCRIPTION_NAME ($SUBSCRIPTION)" \
    'Only direct locks on ppseclogs, ppseclogsitn, ppseclogsneu and sec-p-law.' \
    'Inherited locks, policies, resources and RBAC assignments are never changed.' \
    'Active policies may recreate locks after this temporary removal.' \
    'Requires az login and Microsoft.Authorization/locks/read and /delete access.' \
    'No account switching, credential setup or automatic retries are performed.' \
    'Final counts reconcile planned locks; request errors and new locks are separate.' \
    'Request errors are warnings if all planned locks are verified absent.' \
    '' \
    'Exit codes: 0 = preview completed or removal verified; 1 = failure or' \
    'remaining/new/inherited locks; 2 = usage error; 3 = confirmation cancelled.' \
    '130/143 = interrupted; verify current state before retrying.'
}

heading() {
  printf '\n%b%s%b\n' "$ACCENT" "$1" "$RESET"
}

event() {
  local state="$1" category="$2" marker='ℹ️'
  shift 2
  case "$state" in
    STARTED) marker='▶️' ;;
    PLANNED) marker='📋' ;;
    ABSENT) marker='⏭️' ;;
    WARNING|INHERITED) marker='⚠️' ;;
    REMAINING) marker='🔒' ;;
    FAILED) marker='❌' ;;
    PASSED) marker='✅' ;;
    REMOVED) marker='🔓' ;;
    ACCEPTED) marker='📤' ;;
    CANCELLED|INTERRUPTED) marker='🛑' ;;
    UNVERIFIED) marker='❓' ;;
    'DRY RUN') marker='👁️' ;;
    RESULT) marker='📊' ;;
  esac
  printf '%s %s [%s]: %s\n' "$marker" "$state" "$category" "$*"
}

cleanup() {
  if [[ -n "$WORK_DIR" ]]; then
    rm -rf -- "$WORK_DIR"
  fi
}

diagnostic() {
  event INFO AZURE 'Diagnostic (up to 2000 bytes):'
  head -c 2000 "$WORK_DIR/error"
  printf '\n'
  if [[ $(wc -c < "$WORK_DIR/error") -gt 2000 ]]; then
    event WARNING AZURE 'Diagnostic truncated to 2000 bytes; retry the read-only preview for current state.'
  fi
}

fetch_locks() {
  local destination="$1"
  if ! az lock list --subscription "$SUBSCRIPTION" --output json --only-show-errors \
    > "$destination" 2> "$WORK_DIR/error"; then
    event FAILED DISCOVERY 'Cannot read locks. Check Azure login and lock read permissions.' >&2
    diagnostic >&2
    return 1
  fi
  if ! jq -e --argjson targets "$TARGETS" '
    type == "array" and all(.[];
      (.id | type == "string") and
      (.id | test("^/subscriptions/[^/]+(/[^/]+)*/providers/Microsoft.Authorization/locks/[^/]+$"; "i")) and
      (.id | test("[[:cntrl:]]") | not) and
      (.name | type == "string") and
      ((.id | ascii_downcase | sub("/providers/microsoft.authorization/locks/[^/]+$"; "")) as $owner |
        if any($targets[]; (ascii_downcase | . == $owner or startswith($owner + "/")))
        then (.level == "CanNotDelete" or .level == "ReadOnly")
        else true end)
    )' "$destination" > /dev/null 2>&1; then
    event FAILED DISCOVERY 'Malformed Azure lock response; no further changes will be attempted.' >&2
    return 1
  fi
}

direct_locks() {
  jq --arg scope "$1" '[.[] | select(
    (.id | ascii_downcase | sub("/providers/microsoft.authorization/locks/[^/]+$"; ""))
    == ($scope | ascii_downcase)
  )] | unique_by(.id | ascii_downcase)' "$2"
}

inherited_locks() {
  jq --argjson targets "$TARGETS" '[.[] | . as $lock |
    (.id | ascii_downcase | sub("/providers/microsoft.authorization/locks/[^/]+$"; "")) as $owner |
    select(any($targets[]; (ascii_downcase | startswith($owner + "/")))) |
    $lock] | unique_by(.id | ascii_downcase)' "$1"
}

show_inherited() {
  jq -r '.[] | . as $lock |
    (.id | capture("^(?<scope>.+)/providers/Microsoft.Authorization/locks/[^/]+$"; "i").scope | split("/")) as $scope |
    "  " + (if ($scope | length) == 3 then "Subscription" else "Resource group " + $scope[4] end) +
    ": " + $lock.name + " (" + $lock.level + ")"' "$WORK_DIR/inherited.json"
}

show_ids() {
  local lock_id
  while IFS= read -r lock_id; do
    jq -nr --arg id "$lock_id" '$id | split("/") | "  " + .[-5] + " / " + .[-1]'
  done < "$1"
}

record_request_error() {
  jq -cn --arg id "$1" --arg reason "$2" '{id: $id, reason: $reason}' >> "$WORK_DIR/request-errors"
}

show_request_errors() {
  if [[ -s "$WORK_DIR/request-errors" ]]; then
    heading '⚠️ REQUEST ERRORS | Final lock state is reported separately'
    jq -r '(.id | split("/")) as $parts |
      "  " + $parts[-5] + " / " + $parts[-1] +
      "\n    Resource group: " + $parts[4] +
      "\n    Reason: " + (.reason | gsub("\n"; "\n    ")) +
      "\n    Lock ID: " + .id' "$WORK_DIR/request-errors"
  fi
}

main() {
  local apply=true mode='' no_color=false argument dependency account target count position=0
  local planned=0 absent=0 inherited=0 request_errors=0 removed=0 remaining=0 new_locks=0 lock_id confirmation
  local resource resource_type resource_group lock_description label reason
  for argument in "$@"; do
    case "$argument" in
      --help|-h) usage; return 0 ;;
      --apply|--dry-run)
        if [[ -n "$mode" && "$mode" != "$argument" ]]; then
          event FAILED ARGUMENTS 'Choose either --apply or --dry-run.' >&2
          return 2
        fi
        mode="$argument"
        ;;
      --no-color) no_color=true ;;
      *) event FAILED ARGUMENTS "Unknown option: $argument" >&2; usage >&2; return 2 ;;
    esac
  done
  [[ "$mode" != '--dry-run' ]] || apply=false
  if [[ -t 1 && "$no_color" == false && -z "${NO_COLOR+x}" && "${TERM:-dumb}" != dumb ]]; then
    ACCENT=$'\033[1;36m'
    RESET=$'\033[0m'
  fi
  for dependency in az jq mktemp head wc; do
    if ! command -v "$dependency" > /dev/null 2>&1; then
      event FAILED PREFLIGHT "Missing dependency: $dependency" >&2
      return 1
    fi
  done
  WORK_DIR=$(mktemp -d "${TMPDIR:-/tmp}/security-locks.XXXXXX")
  trap cleanup EXIT
  trap 'event INTERRUPTED EXECUTION "Changes may be partial. Run the preview before retrying." >&2; exit 130' INT
  trap 'event INTERRUPTED EXECUTION "Changes may be partial. Run the preview before retrying." >&2; exit 143' TERM
  TARGETS=$(printf '%s\n' "${RESOURCES[@]}" | jq -Rsc 'split("\n")[:-1]')

  heading '🔐 SECURITY LOCK REMOVAL | PROD-SEC'
  printf 'Subscription: %s (%s)\n' "$SUBSCRIPTION_NAME" "$SUBSCRIPTION"
  if ! account=$(az account show --subscription "$SUBSCRIPTION" --output json --only-show-errors 2> "$WORK_DIR/error"); then
    event FAILED PREFLIGHT 'Subscription unavailable. Check az login and tenant access.' >&2
    diagnostic >&2
    return 1
  fi
  if ! printf '%s' "$account" | jq -e --arg expected "$SUBSCRIPTION" \
    '(.id | ascii_downcase) == $expected and .state == "Enabled"' > /dev/null 2>&1; then
    event FAILED PREFLIGHT 'Unexpected or disabled subscription; refusing to continue.' >&2
    return 1
  fi
  printf 'Azure display name: %s\n' "$(printf '%s' "$account" | jq -r '[.name] | @tsv')"
  fetch_locks "$WORK_DIR/before.json" || return 1
  : > "$WORK_DIR/planned"
  : > "$WORK_DIR/removed"
  : > "$WORK_DIR/remaining"
  : > "$WORK_DIR/new"
  : > "$WORK_DIR/absent"
  : > "$WORK_DIR/request-errors"

  heading '📋 PREVIEW | No changes made'
  printf '  %-16s %-17s %-20s %s\n' 'Resource' 'Type' 'Resource group' 'Lock'
  for target in "${RESOURCES[@]}"; do
    direct_locks "$target" "$WORK_DIR/before.json" > "$WORK_DIR/direct.json"
    count=$(jq 'length' "$WORK_DIR/direct.json")
    if [[ "$count" -eq 0 ]]; then
      absent=$((absent + 1))
      printf '%s\n' "${target##*/}" >> "$WORK_DIR/absent"
    else
      planned=$((planned + count))
      jq -r '.[].id' "$WORK_DIR/direct.json" >> "$WORK_DIR/planned"
    fi
    while IFS=$'\t' read -r resource resource_type resource_group lock_description; do
      printf '  %-16s %-17s %-20s %s\n' "$resource" "$resource_type" "$resource_group" "$lock_description"
    done < <(jq -r --arg scope "$target" '
      ($scope | split("/")) as $parts |
      (if ($parts[6] | ascii_downcase) == "microsoft.storage" then "Storage Account" else "Log Analytics" end) as $type |
      (if length == 0 then ["No direct locks"] else [.[] | .name + " (" + .level + ")"] end)[] as $lock |
      [$parts[-1], $type, $parts[4], $lock] | @tsv' "$WORK_DIR/direct.json")
  done
  inherited_locks "$WORK_DIR/before.json" > "$WORK_DIR/inherited.json"
  inherited=$(jq 'length' "$WORK_DIR/inherited.json")
  printf '\nLocks to remove: %s | Absent at start (resources): %s\n' "$planned" "$absent"
  printf 'Inherited locks: %s\n' "$inherited"
  if [[ "$inherited" -gt 0 ]]; then
    event INHERITED SCOPE 'These locks will NOT be removed and may still block operations:'
    show_inherited
  fi
  event WARNING POLICY 'Active policies may recreate locks. Policies, resources and RBAC assignments are not changed.'
  if [[ "$apply" == false ]]; then
    heading '👁️ DRY RUN RESULTS'
    printf '%s\n' 'No locks removed.' 'Run without --dry-run to review the plan and answer yes/no.'
    return 0
  fi
  if [[ "$planned" -eq 0 ]]; then
    heading '📊 REMOVAL RESULTS | PROD-SEC'
    printf 'Planned: 0 | Removed: 0 | Still present: 0\nAbsent at start (resources): %s | Inherited locks: %s\n' "$absent" "$inherited"
    printf '%s\n' 'No direct locks to remove. No changes made. Resource existence is not checked.'
    [[ "$inherited" -eq 0 ]]
    return
  fi

  printf '\nApply this plan to %s? [yes/no] (default: no): ' "$SUBSCRIPTION_NAME"
  if ! IFS= read -r confirmation || [[ "$confirmation" != 'yes' ]]; then
    event CANCELLED CONFIRM 'No changes made. No locks removed.'
    return 3
  fi
  heading '🔄 REMOVAL'
  position=0
  while IFS= read -r lock_id; do
    position=$((position + 1))
    label=$(jq -nr --arg id "$lock_id" '$id | split("/") | .[-5] + " / " + .[-1]')
    printf '[%s/%s] %s: ' "$position" "$planned" "$label"
    if az lock delete --ids "$lock_id" --subscription "$SUBSCRIPTION" --only-show-errors \
      < /dev/null > /dev/null 2> "$WORK_DIR/error"; then
      printf '%s\n' '📤 Request accepted; verification pending.'
    else
      request_errors=$((request_errors + 1))
      printf '%s\n' '❌ Request failed; details in the final report.'
      reason=$(head -c 2000 "$WORK_DIR/error")
      if [[ $(wc -c < "$WORK_DIR/error") -gt 2000 ]]; then
        reason="$reason [Diagnostic truncated to 2000 bytes.]"
      fi
      record_request_error "$lock_id" "${reason:-Azure CLI returned an error without diagnostic text.}"
    fi
  done < "$WORK_DIR/planned"

  heading '🔎 Checking current state in Azure...'
  if ! fetch_locks "$WORK_DIR/after.json"; then
    heading '📊 REMOVAL RESULTS | PROD-SEC'
    event UNVERIFIED SUMMARY "Verified removals: unknown | Request errors: $request_errors"
    show_request_errors
    printf '%s\n' 'Changes may be partial. Run with --dry-run before retrying.'
    return 1
  fi
  while IFS= read -r lock_id; do
    if jq -e --arg expected "$lock_id" \
      'any(.[]; (.id | ascii_downcase) == ($expected | ascii_downcase))' "$WORK_DIR/after.json" > /dev/null; then
      remaining=$((remaining + 1))
      printf '%s\n' "$lock_id" >> "$WORK_DIR/remaining"
    else
      removed=$((removed + 1))
      printf '%s\n' "$lock_id" >> "$WORK_DIR/removed"
    fi
  done < "$WORK_DIR/planned"
  for target in "${RESOURCES[@]}"; do
    direct_locks "$target" "$WORK_DIR/after.json" > "$WORK_DIR/direct.json"
    jq -r --rawfile planned "$WORK_DIR/planned" '
      ($planned | split("\n") | map(ascii_downcase)) as $ids |
      .[] | .id as $id | select(($ids | index($id | ascii_downcase)) == null) |
      $id' "$WORK_DIR/direct.json" >> "$WORK_DIR/new"
  done
  new_locks=$(( $(wc -l < "$WORK_DIR/new") ))
  inherited_locks "$WORK_DIR/after.json" > "$WORK_DIR/inherited.json"
  inherited=$(jq 'length' "$WORK_DIR/inherited.json")
  heading '📊 REMOVAL RESULTS | PROD-SEC'
  if [[ "$removed" -gt 0 ]]; then
    heading '✅ REMOVED AND VERIFIED'
    show_ids "$WORK_DIR/removed"
  fi
  if [[ "$remaining" -gt 0 ]]; then
    heading '🔒 STILL PRESENT'
    show_ids "$WORK_DIR/remaining"
  fi
  if [[ "$new_locks" -gt 0 ]]; then
    heading '🔒 NEW / UNPLANNED LOCKS | Not deleted'
    show_ids "$WORK_DIR/new"
  fi
  show_request_errors
  if [[ "$absent" -gt 0 ]]; then
    heading '⏭️ NO DIRECT LOCKS AT START'
    while IFS= read -r resource; do printf '  %s\n' "$resource"; done < "$WORK_DIR/absent"
  fi
  if [[ "$inherited" -gt 0 ]]; then
    heading '⚠️ INHERITED LOCKS | Not modified'
    show_inherited
  fi
  printf '\nPlanned: %s | Removed: %s | Still present: %s\n' "$planned" "$removed" "$remaining"
  printf 'New/unplanned locks: %s | Request errors: %s\n' "$new_locks" "$request_errors"
  printf 'Absent at start (resources): %s | Inherited locks: %s\n' "$absent" "$inherited"
  event WARNING POLICY 'This is the current snapshot. Active policies may recreate locks later.'
  if [[ "$remaining" -gt 0 || "$new_locks" -gt 0 || "$inherited" -gt 0 ]]; then
    event WARNING SUMMARY 'PARTIALLY COMPLETED: inspect remaining, new or inherited locks and any request errors.'
    printf '%s\n' 'Successful removals were not rolled back. Run with --dry-run before retrying.'
    return 1
  fi
  if [[ "$request_errors" -gt 0 ]]; then
    event WARNING SUMMARY 'COMPLETED WITH REQUEST WARNINGS: all planned locks are verified absent despite request errors.'
  else
    event PASSED SUMMARY 'All planned removals verified.'
  fi
  event INFO NEXT 'Restore resource protection after the maintenance window.'
}

main "$@"
