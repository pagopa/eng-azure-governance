variable "metrics_logs_types" {
  type        = list(string)
  description = "Diagnostic Settings for metrics logs resource types"
  default = [
    "Microsoft.KeyVault/vaults",
    "Microsoft.Network/virtualNetworkGateways",
    "Microsoft.ContainerService/managedClusters",
    "Microsoft.Network/publicIPAddresses",
    "Microsoft.Network/networkInterfaces",
    "Microsoft.EventHub/Namespace",
    "Microsoft.Network/networkInterfaces",
    "Microsoft.Network/virtualNetworks",
    "Microsoft.Network/azureFirewalls",
    "Microsoft.ContainerInstance/containerGroups",
    "Microsoft.Compute/virtualMachineScaleSets",
    "Microsoft.Network/loadBalancers",
    # "Microsoft.DocumentDB/databaseAccounts", custom
  ]
}

resource "azurerm_policy_definition" "metrics_logs" {
  for_each = toset(var.metrics_logs_types)

  name                = "metricslogs${replace(replace(each.key, "/", ""), "Microsoft.", "")}"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Add Diagnostic Settings for metrics logs to ${replace(replace(each.key, "/", "_"), "Microsoft.", "")}"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Add Diagnostic Settings for metrics logs to ${each.key}",
		      "Severity": "Low"
        }
    }
METADATA

  parameters = <<PARAMETERS
  {
    "diagnosticsSettingName": {
      "type": "String",
      "metadata": {
        "displayName": "Setting name",
        "description": "Name of the diagnostic settings."
      },
      "defaultValue": "MetricsLogs_LogAnalytics"
    },
    "logAnalytics": {
      "type": "String",
      "metadata": {
        "displayName": "Log Analytics workspace",
        "description": "Specify the Log Analytics workspace the Key Vault should be connected to.",
        "strongType": "omsWorkspace",
        "assignPermissions": true
      }
    }
  }
PARAMETERS

  policy_rule = templatefile("./policy_rules/metrics_logs.json", {
    metrics_logs_types                          = each.key,
    roleDefinitionIds_audit_logs_contributor    = data.azurerm_role_definition.audit_logs_contributor.id,
    roleDefinitionIds_log_analytics_contributor = data.azurerm_role_definition.log_analytics_contributor.id,
  })
}
