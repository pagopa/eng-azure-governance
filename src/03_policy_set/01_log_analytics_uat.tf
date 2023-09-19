locals {
  log_analytics_uat = {
    metadata_category_name = "pagopa_uat"
  }
}

resource "azurerm_policy_set_definition" "log_analytics_uat" {
  name                = "log_analytics_uat"
  policy_type         = "Custom"
  display_name        = "PagoPA Log Analytics UAT"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
      "category": "${local.log_analytics_uat.metadata_category_name}",
      "version": "v1.0.0",
      "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_log_analytics.outputs.log_analytics_bound_daily_quota_id
  }
}

output "log_analytics_uat_id" {
  value = azurerm_policy_set_definition.log_analytics_uat.id
}
