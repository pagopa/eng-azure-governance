locals {
  application_insight = {
    metadata_category_name = "pagopa"
  }
}

resource "azurerm_policy_set_definition" "application_insight" {
  name                = "application_insight"
  policy_type         = "Custom"
  display_name        = "PagoPA Application Insight"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.application_insight.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  # Azure Monitor Logs for Application Insights should be linked to a Log Analytics workspace
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/d550e854-df1a-4de9-bf44-cd894b39a95e"
  }
}

output "application_insight_id" {
  value = azurerm_policy_set_definition.application_insight.id
}
