#!/bin/bash



#
# bash .utils/terraform_run_all.sh <Action>
# bash .utils/terraform_run_all.sh init
#

# 'set -e' tells the shell to exit if any of the foreground command fails,
# i.e. exits with a non-zero status.
set -eu

pids=()
ACTION="$1"

policy_folders=(
  'src/01_custom_roles'
  'src/02_policy_audit_logs'
  'src/02_policy_resource_lock'
  'src/02_policy_tags_inherit_from_subscription'
  'src/03_policy_set'
  'src/04_policy_assignments'
)

function rm_terraform {
    find . \( -iname ".terraform*" ! -iname ".terraform-docs*" ! -iname ".terraform-version" \) -print0 | xargs -0 rm -rf
}

echo "[INFO] 🪚  Delete all .terraform folders"
rm_terraform

echo "[INFO] 🏁 Init all policy terraform repos"
az account set -s common

for folder in "${policy_folders[@]}" ; do
    echo "${folder}"
    pushd "$(pwd)/${folder}"
        echo "$folder"
        echo "🔬 folder: $(pwd) in under terraform: $ACTION action"
        terraform "$ACTION" &

        pids+=($!)
    popd
done

# Wait for each specific process to terminate.
# Instead of this loop, a single call to 'wait' would wait for all the jobs
# to terminate, but it would not give us their exit status.
#
for pid in "${pids[@]}"; do
  #
  # Waiting on a specific PID makes the wait command return with the exit
  # status of that process. Because of the 'set -e' setting, any exit status
  # other than zero causes the current shell to terminate with that exit
  # status as well.
  #
  wait "$pid"
done

echo "[INFO] Init governance"
pushd "$(pwd)/src/governance"

    echo "🔬 folder: $(pwd) in under terraform: $ACTION action"
    sh terraform.sh "$ACTION" devopslab &

    pids+=($!)
popd


# Wait for each specific process to terminate.
# Instead of this loop, a single call to 'wait' would wait for all the jobs
# to terminate, but it would not give us their exit status.
#
for pid in "${pids[@]}"; do
  #
  # Waiting on a specific PID makes the wait command return with the exit
  # status of that process. Because of the 'set -e' setting, any exit status
  # other than zero causes the current shell to terminate with that exit
  # status as well.
  #
  wait "$pid"
done
