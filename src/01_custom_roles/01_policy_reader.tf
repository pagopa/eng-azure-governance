resource "azurerm_role_definition" "policy_reader" {
  name        = "PagoPA Policy Reader"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Read policy"

  permissions {
    actions = [
      "Microsoft.PolicyInsights/policyStates/queryResults/read",
    ]
  }
}
