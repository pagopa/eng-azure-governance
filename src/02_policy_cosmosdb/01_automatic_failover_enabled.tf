resource "azurerm_policy_definition" "cosmosdb_automatic_failover_enabled" {
  name                = "cosmosdb_automatic_failover_enabled"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA CosmosDB must have automatic failover enabled"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Enable Automaric Failover for CosmosDB"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/automatic_failover_enabled_parameters.json")

  policy_rule = file("./policy_rules/automatic_failover_enabled_policy.json")

}
