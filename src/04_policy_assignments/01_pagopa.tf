resource "azurerm_management_group_policy_assignment" "pagopa_data_sovereignty_eu" {
  name                 = "pagopadatasovereigntyeu"
  display_name         = "PagoPA Data sovereignty in EU"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.data_sovereignty_eu_id
  management_group_id  = data.azurerm_management_group.pagopa.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}
