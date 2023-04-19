locals {
  event_hub_prod = {
    metadata_category_name = "pagopa_prod"
  }
}

resource "azurerm_policy_set_definition" "event_hub_prod" {
  name                = "event_hub_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Event Hub PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.event_hub_prod.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_event_hub.outputs.eventhub_required_network_id
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_event_hub.outputs.eventhub_allowed_tls_id
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_event_hub.outputs.eventhub_required_zone_redundant_id
  }

}

output "event_hub_prod_id" {
  value = azurerm_policy_set_definition.event_hub_prod.id
}
