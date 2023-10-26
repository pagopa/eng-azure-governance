locals {
  kubernetes_prod = {
    metadata_category_name = "pagopa_prod"
    allowed_container_registry = {
      reference_id = "allowed_container_registry"
      effect       = "Audit"
      regex        = "^([^\\/]+\\.azurecr\\.io|ghcr\\.io\\/pagopa|ghcr\\.io\\/kedacore|mcr\\.microsoft\\.com\\/azure-storage)\\/.+$"
    }
    disable_privileged_containers = {
      reference_id = "disable_privileged_containers_reference_id"
      effect       = "Deny"
    }
    enable_azure_policy_addon = {
      reference_id = "enable_azure_policy_addon_reference_id"
      effect       = "Deny"
    }
    disable_capsysadmin = {
      reference_id = "disable_capsysadmin_reference_id"
      effect       = "Deny"
    }
    enable_defender_profile = {
      reference_id = "enable_defender_profile_reference_id"
      effect       = "Deny"
    }
    disable_api_credentials_automounting = {
      reference_id = "disable_api_credentials_automounting_reference_id"
      effect       = "Audit"
    }
    enforce_apparmor_profile = {
      reference_id = "enforce_apparmor_profile_reference_id"
      effect       = "Audit"
    }
  }
}

resource "azurerm_policy_set_definition" "kubernetes_prod" {
  name                = "kubernetes_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Kubernetes PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.kubernetes_prod.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true",
        "parameterScopes": {
          "${local.kubernetes_prod.allowed_container_registry.reference_id} : ${local.kubernetes_prod.allowed_container_registry.reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.kubernetes_prod.disable_privileged_containers.reference_id} : ${local.kubernetes_prod.disable_privileged_containers.reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.kubernetes_prod.disable_capsysadmin.reference_id} : ${local.kubernetes_prod.disable_capsysadmin.reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.kubernetes_prod.enable_azure_policy_addon.reference_id} : ${local.kubernetes_prod.enable_azure_policy_addon.reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.kubernetes_prod.enable_defender_profile.reference_id} : ${local.kubernetes_prod.enable_defender_profile.reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.kubernetes_prod.disable_api_credentials_automounting.reference_id} : ${local.kubernetes_prod.disable_api_credentials_automounting.reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.kubernetes_prod.enable_defender_profile.reference_id} : ${local.kubernetes_prod.enable_defender_profile.reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.kubernetes_prod.enforce_apparmor_profile.reference_id} : ${local.kubernetes_prod.enforce_apparmor_profile.reference_id}": "${data.azurerm_management_group.pagopa.id}"
        }
    }
METADATA

  # Kubernetes cluster containers should only use allowed images
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/febd0533-8e55-448f-b837-bd0e06f16469"
    reference_id         = local.kubernetes_prod.allowed_container_registry.reference_id
    parameter_values = jsonencode({
      "allowedContainerImagesRegex" : {
        "value" : local.kubernetes_prod.allowed_container_registry.regex
      },
      "effect" : {
        "value" : local.kubernetes_prod.allowed_container_registry.effect
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_kubernetes.outputs.kubernetes_required_image_sha256_id
    parameter_values     = jsonencode({})
  }

  # Kubernetes cluster should not allow privileged containers
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/95edb821-ddaf-4404-9732-666045e056b4"
    reference_id         = local.kubernetes_prod.disable_privileged_containers.reference_id
    parameter_values = jsonencode({
      "effect" : {
        "value" : local.kubernetes_prod.disable_privileged_containers.effect
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_kubernetes.outputs.kubernetes_allowed_kubernetes_version_id
    parameter_values     = jsonencode({})
  }

  # Kubernetes cluster should have 'Standard' SKU
  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_kubernetes.outputs.kubernetes_allowed_sku_id
    parameter_values     = jsonencode({})
  }

  # Kubernetes clusters should not grant CAP_SYS_ADMIN security capabilities
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/d2e7ea85-6b44-4317-a0be-1b951587f626"
    reference_id         = local.kubernetes_prod.disable_capsysadmin.reference_id
    parameter_values = jsonencode({
      "effect" : {
        "value" : local.kubernetes_prod.disable_capsysadmin.effect
      }
    })
  }

  # Azure Policy Add-on for Kubernetes service (AKS) should be installed and enabled on your clusters
  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_kubernetes.outputs.kubernetes_required_policy_addon_id
    reference_id         = local.kubernetes_prod.enable_azure_policy_addon.reference_id
    parameter_values = jsonencode({
      "effect" : {
        "value" : local.kubernetes_prod.enable_azure_policy_addon.effect
      }
    })
  }

  # Azure Kubernetes Service clusters should have Defender profile enabled
  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_kubernetes.outputs.kubernetes_required_defender_profile_id
    reference_id         = local.kubernetes_prod.enable_defender_profile.reference_id
    parameter_values = jsonencode({
      "effect" : {
        "value" : local.kubernetes_prod.enable_defender_profile.effect
      }
    })
  }

  # Kubernetes clusters should disable automounting API credentials
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/423dd1ba-798e-40e4-9c4d-b6902674b423"
    reference_id         = local.kubernetes_prod.disable_api_credentials_automounting.reference_id
    parameter_values = jsonencode({
      "effect" : {
        "value" : local.kubernetes_prod.disable_api_credentials_automounting.effect
      }
    })
  }

  # Kubernetes cluster containers should only use allowed AppArmor profiles
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/511f5417-5d12-434d-ab2e-816901e72a5e"
    reference_id         = local.kubernetes_prod.enforce_apparmor_profile.reference_id
    parameter_values = jsonencode({
      "effect" : {
        "value" : local.kubernetes_prod.enforce_apparmor_profile.effect
      }
    })
  }

}

output "kubernetes_prod_id" {
  value = azurerm_policy_set_definition.kubernetes_prod.id
}
