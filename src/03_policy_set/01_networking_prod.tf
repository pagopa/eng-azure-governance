locals {
  networking_prod = {
    deny_zonal_publicip = {
      reference_id = "deny_zonal_publicip_reference_id"
      effect       = "Audit"
    }
    ddos_protection = {
      reference_id = "ddos_protection_reference_id"
      plan_id      = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-ddos/providers/Microsoft.Network/ddosProtectionPlans/sec-p-ddos-protection"
    }
    vpngw_aad_authentication = {
      reference_id = "vpngw_aad_authentication_reference_id"
      effect       = "Deny"
    }
  }
}

resource "azurerm_policy_set_definition" "networking_prod" {
  name                = "networking_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Networking PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = "pagopa_prod"
    version  = "v1.0.0"
    ASC      = "true"
    parameterScopes = {
      for _, param in local.networking_prod : "${param.reference_id} : ${param.reference_id}" => data.azurerm_management_group.pagopa.id
    }
  })

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_networking.outputs.deny_zonal_publicip_id
    parameter_values     = jsonencode({})
  }

  # Virtual networks should be protected by Azure DDoS Protection Standard
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/94de2ad3-e0c1-4caf-ad78-5d47bbc83d3d"
    reference_id         = local.networking_prod.ddos_protection.reference_id
    parameter_values = jsonencode({
      ddosPlan = {
        value = local.networking_prod.ddos_protection.plan_id
      }
    })
  }

  # VPN gateways should use only Azure Active Directory (Azure AD) authentication for point-to-site users
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/21a6bc25-125e-4d13-b82d-2e19b7208ab7"
    reference_id         = local.networking_prod.vpngw_aad_authentication.reference_id
    parameter_values = jsonencode({
      effect = {
        value = local.networking_prod.vpngw_aad_authentication.effect
      }
    })
  }
}

output "networking_prod_id" {
  value = azurerm_policy_set_definition.networking_prod.id
}
