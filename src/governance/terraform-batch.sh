#!/bin/bash

set -e

SCRIPT_PATH="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CURRENT_DIRECTORY="$(basename "$SCRIPT_PATH")"
ACTION=$1
GIT_DIFF_STRATEGY=$2
GIT_DIFF_PARAM_ONE=$3
ACTIONS_ALLOWED=("apply" "plan" "changes" "refresh")

echo "[INFO] This is the current directory: ${CURRENT_DIRECTORY}"

if [ -z "$ACTION" ]; then
  echo "[ERROR] Missed ACTION: apply, plan"
  exit 1
fi

if ! [[ "${ACTIONS_ALLOWED[*]}" =~ ${ACTION} ]]; then
  echo "[ERROR] 🚧 Only this actions are allowed: ${ACTIONS_ALLOWED[*]}"
  exit 1
fi

if [[ ${GIT_DIFF_STRATEGY} == "time" ]]; then
  if [[ -z ${GIT_DIFF_PARAM_ONE} ]]; then
    echo "[ERROR] 🚧 time strategy need a number of days"
    exit 1
  fi

  SUBSCRIPTIONS_CHANGED="$(git diff  --dirstat=files,0 $(git rev-list -n1 --before="${GIT_DIFF_PARAM_ONE} day ago" main) | perl -n -e'/subscriptions\/(.*)/ && print $1' | perl -ple 'chop')"
else
  SUBSCRIPTIONS_CHANGED="$(git diff  --dirstat=files,0 | perl -n -e'/subscriptions\/(.*)/ && print $1' | perl -ple 'chop')"
fi

LIST_SUBSCRIPTIONS_CHANGED="$(echo "$SUBSCRIPTIONS_CHANGED" | tr '/' '\n')"

# shellcheck disable=SC2028
echo "📳 Subscriptions that will be changed: \n${LIST_SUBSCRIPTIONS_CHANGED} \n"
if [[ ${ACTION} == "changes" ]]; then
  exit 0
fi

for dir in ${LIST_SUBSCRIPTIONS_CHANGED}
do
    #check if the folder contains a valid terraform file
    if [ -f "$SCRIPT_PATH/subscriptions/${dir}/terraform.tfvars" ]; then

        # shellcheck disable=SC2028
        echo "🟨 started: Terraform $ACTION on ${dir} \n"

        if [[ "${ACTION}" == "apply" ]]; then
          sh terraform.sh "${ACTION}" "${dir}" -auto-approve -compact-warnings
        else
          sh terraform.sh "${ACTION}" "${dir}" -compact-warnings
        fi

        # shellcheck disable=SC2028
        echo "✅ completed: Terraform $ACTION on ${dir} \n"
    fi
done
