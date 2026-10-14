resource "azurerm_policy_definition" "cosmosdb_required_backup_policy" {
  name                = "cosmosdb_required_backup_policy"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA CosmosDB required backup policy"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use required backup policy for CosmosDB"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/required_backup_policy_parameters.json")

  policy_rule = file("./policy_rules/required_backup_policy_policy.json")

}
