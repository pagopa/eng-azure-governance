variable "redis_prod" {
  type = object({
    listofallowedskuname     = list(string)
    listofallowedskucapacity = list(string)
  })
  default = {
    listofallowedskuname     = ["Standard", "Premium"]
    listofallowedskucapacity = ["0", "1", "2"]
  }
  description = "List of redis policy set parameters"
}

resource "azurerm_policy_set_definition" "redis_prod" {
  name                = "redis_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Redis PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "pagopa_prod",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_redis.outputs.redis_allowed_versions_id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_redis.outputs.redis_allowed_tls_id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_redis.outputs.redis_disable_nosslport_id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_redis.outputs.redis_allowed_sku_id
    reference_id         = local.redis.listofallowedsku
    parameter_values     = <<VALUE
    {
      "listOfAllowedSkuName": {
        "value": ${jsonencode(var.redis_prod.listofallowedskuname)}
      },
      "listOfAllowedSkuCapacity": {
        "value": ${jsonencode(var.redis_prod.listofallowedskucapacity)}
      }
    }
    VALUE
  }

  # Azure Cache for Redis should disable public network access
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/470baccb-7e51-4549-8b1a-3e5be069f663"
    parameter_values     = jsonencode({})
  }

  # Azure Cache for Redis should use private link
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/7803067c-7d34-46e3-8c79-0ca68fc4036d"
    parameter_values     = jsonencode({})
  }

}

output "redis_prod_id" {
  value = azurerm_policy_set_definition.redis_prod.id
}
