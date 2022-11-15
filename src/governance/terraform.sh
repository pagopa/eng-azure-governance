#!/bin/bash
set -e

#
# 💡 How to use
# sh terraform.sh apply <subscription name>
# sh terraform.sh apply dev-pagopa
#

ACTION=$1
DIR_SUBSCRIPTION=$2

SCRIPT_PATH="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CURRENT_DIRECTORY="$(basename "$SCRIPT_PATH")"
shift 2
other="$*"
storage_account_name=""
location=""
location_short="weu"
# must be subscription in lower case

echo "[INFO] This is the current directory: ${CURRENT_DIRECTORY}"

if [ -z "$ACTION" ]; then
  echo "[ERROR] Missed ACTION: init, apply, plan"
  exit 0
fi

if [ -z "$DIR_SUBSCRIPTION" ]; then
  echo "[ERROR] DIR_SUBSCRIPTION should be: dev, uat or prod."
  exit 0
fi

#
# 🏁 Source & init shell
#

# shellcheck source=/dev/null
source "${SCRIPT_PATH}/subscriptions/$DIR_SUBSCRIPTION/backend.ini"

# Subscription set
az account set -s "${DIR_SUBSCRIPTION}"

# if using cygwin, we have to transcode the WORKDIR
if [[ $WORKDIR == /cygdrive/* ]]; then
  WORKDIR=$(cygpath -w $WORKDIR)
fi


#
# 🌎 Terraform
#
if echo "init plan apply refresh import output state taint destroy" | grep -w "$ACTION" > /dev/null; then
  if [ "$ACTION" = "init" ]; then
    echo "[INFO] 🎬 init tf on DIR_SUBSCRIPTION: ${DIR_SUBSCRIPTION}"
    terraform "$ACTION" -backend-config="storage_account_name=${storage_account_name}" "$other"
  elif [ "$ACTION" = "output" ] || [ "$ACTION" = "state" ] || [ "$ACTION" = "taint" ]; then
    # init terraform backend
    terraform init -reconfigure -backend-config="storage_account_name=${storage_account_name}"
    terraform "$ACTION" "$other"
  else
    # init terraform backend
    echo "[INFO] 🎬 init tf on DIR_SUBSCRIPTION: ${DIR_SUBSCRIPTION}"
    terraform init \
    -reconfigure \
    -backend-config="storage_account_name=${storage_account_name}"

    echo "[INFO] ⌛️ run tf with: ${ACTION} on DIR_SUBSCRIPTION: ${DIR_SUBSCRIPTION} and other: >${other}<"
    terraform "${ACTION}" \
    -compact-warnings \
    -var-file="./subscriptions/${DIR_SUBSCRIPTION}/terraform.tfvars" \
    -var location="${location}" -var location_short="${location_short}" \
    $other

    echo "[INFO] ✅ completed tf with: ${ACTION} on DIR_SUBSCRIPTION: ${DIR_SUBSCRIPTION} and other: >${other}<"
  fi
else
    echo "[ERROR] 🚧 ACTION not allowed."
    exit 1
fi
