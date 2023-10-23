locals {
  key_vault_prod = {
    metadata_category_name = "pagopa_prod"
  }
}

resource "azurerm_policy_set_definition" "key_vault_prod" {
  name                = "key_vault_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Kay Vault PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.key_vault_prod.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  # Key vaults should have deletion protection enabled
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/0b60c0b2-2dc2-4e1c-b5c9-abbed971de53"
  }

  # Key vaults should have soft delete enabled
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/1e66c121-a66a-4b1f-9b83-0fd99bf0fc2d"
  }

}

output "key_vault_prod_id" {
  value = azurerm_policy_set_definition.key_vault_prod.id
}