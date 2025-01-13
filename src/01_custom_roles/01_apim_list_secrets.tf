resource "azurerm_role_definition" "apim_list_secrets" {
  name        = "PagoPA API Management Service List Secrets"
  scope       = data.azurerm_management_group.pagopa.id
  description = "List-only access to API Management secrets"

  permissions {
    actions = [
      "Microsoft.ApiManagement/service/*/listSecrets/action",
    ]
  }
}