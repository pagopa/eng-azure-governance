#!/bin/bash

set -e

action=$1
shift 1
other=$@

subscription="MOCK_VALUE"

case $action in
    "init" | "apply" | "plan" | "destroy" )
        # shellcheck source=/dev/null
        if [ -e "./backend.ini" ]; then
          source ./backend.ini
        else
          echo "Error: no backend.ini found!"
          exit 1
        fi

        az account set -s "${subscription}"
        SUBSCRIPTION_ID=$(az account show --query id -o tsv)
        export TF_VAR_subscription_id="${SUBSCRIPTION_ID}"

        terraform init
        terraform "$action" $other
        ;;
    * )
        echo "Missed action: init, apply, plan, destroy"
        exit 1
        ;;
esac
