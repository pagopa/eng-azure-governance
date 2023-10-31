locals {
  networking_prod = {
    metadata_category_name = "pagopa_prod"
    deny_zonal_publicip = {
      reference_id = "deny_zonal_publicip_reference_id"
      effect       = "Audit"
    }
    ddos_protection = {
      reference_id = "ddos_protection_reference_id"
      plan_id      = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-ddos/providers/Microsoft.Network/ddosProtectionPlans/sec-p-ddos-protection"
    }
  }
}

resource "azurerm_policy_set_definition" "networking_prod" {
  name                = "networking_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Networking PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.networking_prod.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true",
        "parameterScopes": {
          "${local.networking_prod.ddos_protection.reference_id} : ${local.networking_prod.ddos_protection.reference_id}": "${data.azurerm_management_group.pagopa.id}"
        }
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_networking.outputs.deny_zonal_publicip_id
    parameter_values     = jsonencode({})
  }

  # Virtual networks should be protected by Azure DDoS Protection Standard
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/94de2ad3-e0c1-4caf-ad78-5d47bbc83d3d"
    reference_id         = local.networking_prod.ddos_protection.reference_id
    parameter_values     = <<VALUE
    {
      "ddosPlan": {
        "value": ${jsonencode(local.networking_prod.ddos_protection.plan_id)}
      }
    }
    VALUE
  }
}

output "networking_prod_id" {
  value = azurerm_policy_set_definition.networking_prod.id
}
