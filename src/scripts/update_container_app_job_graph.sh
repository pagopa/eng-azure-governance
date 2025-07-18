#!/bin/bash

set -euo pipefail

if ! az extension show --name containerapp &>/dev/null; then
  az extension add --name containerapp
fi

if ! az extension show --name resource-graph &>/dev/null; then
  az extension add --name resource-graph
fi

JOBS=$(az graph query -q "
resources
| where type == 'microsoft.app/jobs'
| where properties.configuration.eventTriggerConfig.scale.minExecutions != '0'
| where properties.template.containers[0].image startswith 'ghcr.io/pagopa/github-self-hosted-runner-azure'
| project name, resourceGroup, subscriptionId, minExecutions=properties.configuration.eventTriggerConfig.scale.minExecutions, maxExecutions=properties.configuration.eventTriggerConfig.scale.maxExecutions, image=properties.template.containers[0].image
" --first 1000 -o json)

COUNT=$(echo "$JOBS" | jq '.data | length')
if [[ "$COUNT" -eq 0 ]]; then
  echo "⚠️ Nothing job with minExecutions != 0 and target image."
  exit 0
fi

echo "$JOBS" | jq -c '.data[]' | while read -r job; do

  NAME=$(echo "$job" | jq -r '.name')
  RG=$(echo "$job" | jq -r '.resourceGroup')
  SUBSCRIPTION=$(echo "$job" | jq -r '.subscriptionId')
  MIN_EXEC=$(echo "$job" | jq -r '.minExecutions // 0')
  MAX_EXEC=$(echo "$job" | jq -r '.maxExecutions // 0')
  IMAGE=$(echo "$job" | jq -r '.image // ""')

  echo "[DEBUG] name=$NAME, rg=$RG, sub=$SUBSCRIPTION, min_exec=$MIN_EXEC, max_exec=$MAX_EXEC, image=$IMAGE"

  az containerapp job update \
    --name "$NAME" \
    --resource-group "$RG" \
    --min-executions "0" \
    --max-executions "$MAX_EXEC" \
    --subscription "$SUBSCRIPTION" \
    --query "{name: name}" \
    --output json

done

echo "🎉 Done. Total jobs $COUNT"
