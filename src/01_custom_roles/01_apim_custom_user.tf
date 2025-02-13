resource "azurerm_role_definition" "apim_custom_user" {
  name        = "PagoPA API Management Custom User"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Custom role for managing API Management users, groups, subscriptions, and secrets."

  permissions {
    actions = [
      # Subscription
      "Microsoft.ApiManagement/service/subscriptions/write",
      "Microsoft.ApiManagement/service/subscriptions/read",
      "Microsoft.ApiManagement/service/workspaces/subscriptions/write",
      "Microsoft.ApiManagement/service/workspaces/subscriptions/read",

      # Secrets and Keys
      "Microsoft.ApiManagement/service/tenant/write",
      "Microsoft.ApiManagement/service/*/regeneratePrimaryKey/action",
      "Microsoft.ApiManagement/service/*/regenerateSecondaryKey/action",
      "Microsoft.ApiManagement/service/*/listSecrets/action",

      # User and Group
      "Microsoft.ApiManagement/service/users/read",
      "Microsoft.ApiManagement/service/users/write",
      "Microsoft.ApiManagement/service/users/delete",
      "Microsoft.ApiManagement/service/groups/read",
      "Microsoft.ApiManagement/service/groups/write",
      "Microsoft.ApiManagement/service/groups/delete",
      "Microsoft.ApiManagement/service/groups/users/read",
      "Microsoft.ApiManagement/service/groups/users/write",
      "Microsoft.ApiManagement/service/groups/users/delete",

      # Product
      "Microsoft.ApiManagement/service/products/read"
    ]
  }
}