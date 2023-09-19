locals {
  log_analytics_prod = {
    metadata_category_name = "pagopa_prod"
  }
}

resource "azurerm_policy_set_definition" "log_analytics_prod" {
  name                = "log_analytics_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Log Analytics PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
      "category": "${local.log_analytics_prod.metadata_category_name}",
      "version": "v1.0.0",
      "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_log_analytics.outputs.log_analytics_unbound_daily_quota_id
  }
}

output "log_analytics_prod_id" {
  value = azurerm_policy_set_definition.log_analytics_prod.id
}
