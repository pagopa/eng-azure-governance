#!/bin/bash
az extension add --name containerapp --upgrade

# Image target
TARGET_IMAGE="ghcr.io/pagopa/github-self-hosted-runner-azure:latest"

# Subscription list
SUBSCRIPTIONS=$(az account list --query '[].{name:name, id:id}' -o json)
#SUBSCRIPTIONS=$(az account list --query "[?id=='ac17914c-79bf-48fa-831e-1359ef74c1d5'].{name:name, id:id}" -o json)


TOTAL_MATCHED=0

for row in $(echo "$SUBSCRIPTIONS" | jq -r '.[] | @base64'); do
  _jq() {
    echo "$row" | base64 --decode | jq -r "$1"
  }

  SUBSCRIPTION_NAME=$(_jq '.name')
  SUBSCRIPTION_ID=$(_jq '.id')

  echo "--> 🔁 Switching to subscription: $SUBSCRIPTION_NAME ($SUBSCRIPTION_ID)"
  az account set --subscription "$SUBSCRIPTION_ID"

  # List of Container app jobs in current subscription
  JOBS=$(az containerapp job list --query "[].{name:name, rg:resourceGroup}" -o json)

  if [ "$(echo "$JOBS" | jq length)" -eq 0 ]; then
    echo "--> ⚠️  No Container App Jobs found in $SUBSCRIPTION_NAME"
    continue
  fi

  for job_row in $(echo "$JOBS" | jq -r '.[] | @base64'); do
    _jobjq() {
      echo "$job_row" | base64 --decode | jq -r "$1"
    }

    JOB_NAME=$(_jobjq '.name')
    RG_NAME=$(_jobjq '.rg')

    # Get Job definition
    JOB_DEF=$(az containerapp job show --name "$JOB_NAME" --resource-group "$RG_NAME" -o json)

    IMAGE=$(echo "$JOB_DEF" | jq -r '.properties.template.containers[0].image')
    EXEC=$(echo "$JOB_DEF" | jq -r '
  if .properties.configuration.eventTriggerConfig and .properties.configuration.eventTriggerConfig.scale then
    .properties.configuration.eventTriggerConfig.scale.minExecutions // 0
  else
    0
  end
')


    if [ "$EXEC" != "0" ] && [ "$IMAGE" = "$TARGET_IMAGE" ]; then
      #echo "--> ✅ [$SUBSCRIPTION_NAME] Updating job: $JOB_NAME (image: $IMAGE)"
      echo "--> ✅ [$SUBSCRIPTION_NAME] job with min-exec !=0: $JOB_NAME (image: $IMAGE)"
      TEMPLATE=$(echo "$JOB_DEF" | jq -c '.properties.template')
      echo 'Template:'$TEMPLATE
      #az containerapp job update \
      #  --name "$JOB_NAME" \
      #  --resource-group "$RG_NAME" \
      #  --min-executions 0 \
      #  --only-show-errors

      TOTAL_MATCHED=$((TOTAL_MATCHED + 1))
    else
      echo "--> ⏭️  Skipping job: $JOB_NAME (image: $IMAGE)"
    fi
  done
done

echo "🎉 Done. Total jobs updated across all subscriptions: $TOTAL_MATCHED"
