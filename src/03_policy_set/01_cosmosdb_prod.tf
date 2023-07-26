locals {
  cosmosdb_prod = {
    metadata_category_name = "pagopa_prod"
  }
}

resource "azurerm_policy_set_definition" "cosmosdb_prod" {
  name                = "cosmosdb_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA CosmosDB PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.cosmosdb_prod.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_cosmosdb.outputs.cosmosdb_required_network_id
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_cosmosdb.outputs.cosmosdb_allowed_tls_id
  }

}

output "cosmosdb_prod_id" {
  value = azurerm_policy_set_definition.cosmosdb_prod.id
}
