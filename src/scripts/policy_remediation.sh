az extension show --name account || az extension add --name account
subscriptions=$(az account subscription list --query "[].subscriptionId" -o tsv)
policySetIds=(
    '/providers/Microsoft.Management/managementGroups/pagopa/providers/Microsoft.Authorization/policySetDefinitions/audit_logs'
    '/providers/Microsoft.Management/managementGroups/pagopa/providers/Microsoft.Authorization/policySetDefinitions/resource_lock'
)

for subscriptionId in $subscriptions; do
    az account set --subscription $subscriptionId
    az account set --subscription PROD-P4PA

    # Loop through each policy set ID
    for policySetId in "${policySetIds[@]}"; do

        # Get the list of policy assignments and filter by the policy set
        policyAssignments=$(az policy assignment list --query "[?policyDefinitionId=='$policySetId'].name" -o tsv)

        # Loop through each policy assignment and check compliance state
        for policyAssignmentName in $policyAssignments; do
            echo "Processing policy assignment: $policyAssignmentName"

            # Get the compliance state of resources for this policy assignment
            complianceStates=$(az policy state list --policy-assignment $policyAssignmentName --query "[?complianceState=='NonCompliant'].policyDefinitionReferenceId" -o tsv | sort | uniq)

            # Check if there are any non-compliant resources
            if [[ -z "$complianceStates" ]]; then
                echo "No resources found for policy assignment: $policyAssignmentName"
            else
                for policyDefinitionReferenceId in $complianceStates; do
                    echo "Remediating resource for policy definition: $policyDefinitionReferenceId"
                    # Command to remediate the resource
                    timestamp=$(date +%s)
                    # echo "DRY RUN: az policy remediation create --name "remediationTask$timestamp" --policy-assignment $policyAssignmentName --definition-reference-id $policyDefinitionReferenceId"
                    az policy remediation create --name "remediationTask$timestamp" --policy-assignment $policyAssignmentName --definition-reference-id $policyDefinitionReferenceId
                done
            fi
        done
    done
    exit 0
done


