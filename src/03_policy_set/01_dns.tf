locals {
  dns = {
    metadata_category_name = "pagopa_global"
  }
}

resource "azurerm_policy_set_definition" "dns" {
  name                = "dns"
  policy_type         = "Custom"
  display_name        = "PagoPA DNS"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.dns.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_dns.outputs.dns_required_caa_record_id
    parameter_values     = jsonencode({})
  }

}

output "dns_id" {
  value = azurerm_policy_set_definition.dns.id
}
