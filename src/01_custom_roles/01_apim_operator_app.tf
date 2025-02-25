resource "azurerm_role_definition" "apim_operator_app" {
  name        = "PagoPA API Management Operator App"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Custom role for managing API Management users, groups, subscriptions, and secrets."

  permissions {
    actions = [
      "Microsoft.ApiManagement/service/*/read",
      "Microsoft.ApiManagement/service/read",
      "Microsoft.ApiManagement/service/write",
      "Microsoft.Authorization/*/read",
      "Microsoft.ResourceHealth/availabilityStatuses/read",
      "Microsoft.Resources/subscriptions/resourceGroups/read",

      # Subscription
      "Microsoft.ApiManagement/service/subscriptions/write",
      "Microsoft.ApiManagement/service/workspaces/subscriptions/write",

      # Secrets and Keys
      "Microsoft.ApiManagement/service/tenant/write",
      "Microsoft.ApiManagement/service/*/regeneratePrimaryKey/action",
      "Microsoft.ApiManagement/service/*/regenerateSecondaryKey/action",
      "Microsoft.ApiManagement/service/*/listSecrets/action",

      # User and Group
      "Microsoft.ApiManagement/service/users/write",
      "Microsoft.ApiManagement/service/users/delete",
      "Microsoft.ApiManagement/service/groups/write",
      "Microsoft.ApiManagement/service/groups/delete",
      "Microsoft.ApiManagement/service/groups/users/read",
      "Microsoft.ApiManagement/service/groups/users/write",
      "Microsoft.ApiManagement/service/groups/users/delete",

      # Deployments
      "Microsoft.ApiManagement/service/managedeployments/action",
      "Microsoft.Resources/deployments/*",
    ]
  }
}