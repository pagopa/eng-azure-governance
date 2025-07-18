variable "redis_dev" {
  type = object({
    listofallowedskuname     = list(string)
    listofallowedskucapacity = list(string)
  })
  default = {
    listofallowedskuname     = ["Basic"]
    listofallowedskucapacity = ["0", "1"]
  }
  description = "List of redis policy set parameters"
}

resource "azurerm_policy_set_definition" "redis_dev" {
  name                = "redis_dev"
  policy_type         = "Custom"
  display_name        = "PagoPA Redis DEV"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = "pagopa_dev"
    version  = "v1.0.0"
    ASC      = "true"
  })

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
    parameter_values = jsonencode({
      listOfAllowedSkuName = {
        value = var.redis_dev.listofallowedskuname
      }
      listOfAllowedSkuCapacity = {
        value = var.redis_dev.listofallowedskucapacity
      }
    })
  }

}

output "redis_dev_id" {
  value = azurerm_policy_set_definition.redis_dev.id
}
