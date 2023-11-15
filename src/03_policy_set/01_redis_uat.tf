variable "redis_uat" {
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

resource "azurerm_policy_set_definition" "redis_uat" {
  name                = "redis_uat"
  policy_type         = "Custom"
  display_name        = "PagoPA Redis UAT"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "pagopa_uat",
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
        "value": ${jsonencode(var.redis_uat.listofallowedskuname)}
      },
      "listOfAllowedSkuCapacity": {
        "value": ${jsonencode(var.redis_uat.listofallowedskucapacity)}
      }
    }
    VALUE
  }

}

output "redis_uat_id" {
  value = azurerm_policy_set_definition.redis_uat.id
}
