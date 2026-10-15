resource "azurerm_role_definition" "policy_remediator" {
  name        = "PagoPA Policy Remediator"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Remediate policy"

  permissions {
    actions = [
      "Microsoft.PolicyInsights/remediations/write",
    ]
  }
}
