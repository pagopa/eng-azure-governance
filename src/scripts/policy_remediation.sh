#!/usr/bin/env bash
#
# Purpose: Create Azure Policy remediation tasks for non-compliant resources.
# Usage examples:
#   ./src/scripts/policy_remediation.sh

set -euo pipefail

if ! command -v az >/dev/null 2>&1; then
    echo "❌ Azure CLI not found in PATH."
    exit 1
fi

echo "ℹ️ Ensuring Azure CLI account extension is available"
az extension show --name account >/dev/null 2>&1 || az extension add --name account

echo "ℹ️ Listing subscriptions"
subscriptions=$(az account subscription list --query "[].subscriptionId" -o tsv)
policySetIds=(
    '/providers/Microsoft.Management/managementGroups/pagopa/providers/Microsoft.Authorization/policySetDefinitions/audit_logs'
    '/providers/Microsoft.Management/managementGroups/pagopa/providers/Microsoft.Authorization/policySetDefinitions/resource_lock'
)

for subscriptionId in $subscriptions; do
    echo "ℹ️ Processing subscription: $subscriptionId"
    az account set --subscription "$subscriptionId"

    # Loop through each policy set ID
    for policySetId in "${policySetIds[@]}"; do

        # Get the list of policy assignments and filter by the policy set
        policyAssignments=$(az policy assignment list --query "[?policyDefinitionId=='$policySetId'].name" -o tsv)

        # Loop through each policy assignment and check compliance state
        for policyAssignmentName in $policyAssignments; do
            echo "ℹ️ Processing policy assignment: $policyAssignmentName"

            # Get the compliance state of resources for this policy assignment
            complianceStates=$(az policy state list --policy-assignment $policyAssignmentName --query "[?complianceState=='NonCompliant'].policyDefinitionReferenceId" -o tsv | sort | uniq)

            # Check if there are any non-compliant resources
            if [[ -z "$complianceStates" ]]; then
                echo "✅ No non-compliant resources found for policy assignment: $policyAssignmentName"
            else
                for policyDefinitionReferenceId in $complianceStates; do
                    echo "ℹ️ Remediating policy definition: $policyDefinitionReferenceId"
                    # Command to remediate the resource
                    timestamp=$(date +%s)
                    # echo "DRY RUN: az policy remediation create --name "remediationTask$timestamp" --policy-assignment $policyAssignmentName --definition-reference-id $policyDefinitionReferenceId"
                    az policy remediation create --name "remediationTask$timestamp" --policy-assignment "$policyAssignmentName" --definition-reference-id "$policyDefinitionReferenceId"
                done
            fi
        done
    done
done
