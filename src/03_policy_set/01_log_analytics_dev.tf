locals {
  log_analytics_dev = {
    metadata_category_name = "pagopa_dev"
  }
}

resource "azurerm_policy_set_definition" "log_analytics_dev" {
  name                = "log_analytics_dev"
  policy_type         = "Custom"
  display_name        = "PagoPA Log Analytics DEV"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
      "category": "${local.log_analytics_dev.metadata_category_name}",
      "version": "v1.0.0",
      "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_log_analytics.outputs.log_analytics_bound_daily_quota_id
  }
}

output "log_analytics_dev_id" {
  value = azurerm_policy_set_definition.log_analytics_dev.id
}
