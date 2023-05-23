locals {
  redis_prod = {
    metadata_category_name = "pagopa_prod"
  }
}

resource "azurerm_policy_set_definition" "redis_prod" {
  name                = "redis_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Redis PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.redis_prod.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_redis.outputs.redis_allowed_versions_id
  }

}

output "redis_prod_id" {
  value = azurerm_policy_set_definition.redis_prod.id
}
