resource "azurerm_role_assignment" "prod_policy_reader" {
  scope                = data.azurerm_management_group.pagopa.id
  role_definition_name = "PagoPA Resource Policy Reader"
  principal_id         = azurerm_user_assigned_identity.prod.principal_id
}

resource "azurerm_role_assignment" "prod_policy_remediator" {
  scope                = data.azurerm_management_group.pagopa.id
  role_definition_name = "PagoPA Resource Policy Remediator"
  principal_id         = azurerm_user_assigned_identity.prod.principal_id
}

resource "azurerm_role_assignment" "prod_management_group_reader" {
  scope                = data.azurerm_management_group.pagopa.id
  role_definition_name = "Management Group Reader"
  principal_id         = azurerm_user_assigned_identity.prod.principal_id
}

resource "azurerm_role_assignment" "prod_tfinforg" {
  scope                = data.azurerm_storage_account.tfinforg.id
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.prod.principal_id
}
