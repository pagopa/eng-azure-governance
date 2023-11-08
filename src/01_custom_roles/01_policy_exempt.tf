resource "azurerm_role_definition" "policy_exempt" {
  name        = "PagoPA Policy Exempt"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Exempt policy"

  permissions {
    actions = [
      "Microsoft.Authorization/policyAssignments/exempt/action",
    ]
  }
}
