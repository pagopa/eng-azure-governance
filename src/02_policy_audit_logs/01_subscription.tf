resource "azurerm_policy_definition" "audit_logs_subscription_log_analytics" {
  name                = "audit_logs_subscription_log_analytics"
  policy_type         = "Custom"
  mode                = "All"
  display_name        = "PagoPA Add Diagnostic Settings for audit logs for Subscription to Log Analytics workspace"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Add Diagnostic Settings for audit logs for Subscription to Log Analytics workspace",
		      "Severity": "High"
        }
    }
METADATA

  parameters = file("./policy_rules/subscription_log_analytics_parameters.json")

  policy_rule = templatefile("./policy_rules/subscription_log_analytics.json", {
    roleDefinitionIds_audit_logs_contributor    = data.azurerm_role_definition.audit_logs_contributor.id,
    roleDefinitionIds_log_analytics_contributor = data.azurerm_role_definition.log_analytics_contributor.id,
  })

}

resource "azurerm_policy_definition" "audit_logs_subscription_storage_account" {
  name                = "audit_logs_subscription_storage_account"
  policy_type         = "Custom"
  mode                = "All"
  display_name        = "PagoPA Add Diagnostic Settings for audit logs for Subscription to Storage Account"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Add Diagnostic Settings for audit logs for Subscription to Storage Account",
		      "Severity": "High"
        }
    }
METADATA

  parameters = file("./policy_rules/subscription_storage_parameters.json")

  policy_rule = templatefile("./policy_rules/subscription_storage_account.json", {
    roleDefinitionIds_audit_logs_contributor    = data.azurerm_role_definition.audit_logs_contributor.id,
    roleDefinitionIds_log_analytics_contributor = data.azurerm_role_definition.log_analytics_contributor.id,
  })

}
