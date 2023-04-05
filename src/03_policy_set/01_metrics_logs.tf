variable "metrics_logs_pci_workspace_id" {
  type        = string
  default     = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourcegroups/sec-p-sentinel/providers/microsoft.operationalinsights/workspaces/sec-p-law"
  description = "description"
}

locals {
  metrics_logs = {
    metadata_category_name = "pagopa_pci"
  }
}

resource "azurerm_policy_set_definition" "metrics_logs" {
  name                = "metrics_logs"
  policy_type         = "Custom"
  display_name        = "PagoPA Metrics Logs"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.metrics_logs.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  parameters = <<PARAMETERS
    {
        "logAnalyticsId": {
            "type": "String",
            "metadata": {
                "description": "Metrics Logs workspace Id",
                "displayName": "Metrics Logs workspace Id"
            },
            "defaultValue": "${var.metrics_logs_pci_workspace_id}"
        }
    }
PARAMETERS

  dynamic "policy_definition_reference" {
    for_each = data.terraform_remote_state.policy_metrics_logs.outputs.policy_ids
    content {
      policy_definition_id = policy_definition_reference.value
      reference_id         = replace(replace(policy_definition_reference.value, "/providers/Microsoft.Management/managementGroups/pagopa/providers/Microsoft.Authorization/policyDefinitions/metricslogs", ""), "/", "")
      parameter_values     = <<VALUE
      {
        "logAnalytics": {
          "value": "[parameters('logAnalyticsId')]"
        }
      }
    VALUE
    }
  }
}

output "metrics_logs_id" {
  value = azurerm_policy_set_definition.metrics_logs.id
}
