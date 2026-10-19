resource "azurerm_policy_set_definition" "event_hub_prod" {
  name                = "event_hub_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Event Hub PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = "pagopa_prod"
    version  = "v1.0.0"
    ASC      = "true"
  })

  policy_definition_reference {
    policy_definition_id = data.azurerm_policy_definition.this["eventhub_required_network"].id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.azurerm_policy_definition.this["eventhub_allowed_tls"].id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.azurerm_policy_definition.this["eventhub_required_zone_redundant"].id
    parameter_values     = jsonencode({})
  }

}

output "event_hub_prod_id" {
  value = azurerm_policy_set_definition.event_hub_prod.id
}
