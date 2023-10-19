locals {
  kubernetes_prod = {
    metadata_category_name                     = "pagopa_prod"
    allowed_container_registry_reference_id    = "allowed_container_registry"
    allowed_container_registry_effect          = "Audit"
    allowed_container_registry_regex           = "^([^\\/]+\\.azurecr\\.io|ghcr\\.io\\/pagopa|ghcr\\.io\\/kedacore|mcr\\.microsoft\\.com\\/azure-storage)\\/.+$"
    disable_privileged_containers_reference_id = "disable_privileged_containers_reference_id"
    disable_privileged_containers_effect       = "Deny"
    enable_azure_policy_addon = {
      reference_id = "enable_azure_policy_addon_reference_id"
      effect       = "Audit"
    }
    disable_capsysadmin = {
      reference_id = "disable_capsysadmin_reference_id"
      effect       = "Deny"
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
          "${local.kubernetes_prod.allowed_container_registry_reference_id} : ${local.kubernetes_prod.allowed_container_registry_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.kubernetes_prod.disable_privileged_containers_reference_id} : ${local.kubernetes_prod.disable_privileged_containers_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.kubernetes_prod.disable_capsysadmin.reference_id} : ${local.kubernetes_prod.disable_capsysadmin.reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.kubernetes_prod.enable_azure_policy_addon.reference_id} : ${local.kubernetes_prod.enable_azure_policy_addon.reference_id}": "${data.azurerm_management_group.pagopa.id}"
        }
    }
METADATA

  # Kubernetes cluster containers should only use allowed images
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/febd0533-8e55-448f-b837-bd0e06f16469"
    reference_id         = local.kubernetes_prod.allowed_container_registry_reference_id
    parameter_values = jsonencode({
      "allowedContainerImagesRegex" : {
        "value" : local.kubernetes_prod.allowed_container_registry_regex
      },
      "effect" : {
        "value" : local.kubernetes_prod.allowed_container_registry_effect
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_kubernetes.outputs.kubernetes_required_image_sha256_id
  }

  # Kubernetes cluster should not allow privileged containers
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/95edb821-ddaf-4404-9732-666045e056b4"
    reference_id         = local.kubernetes_prod.disable_privileged_containers_reference_id
    parameter_values = jsonencode({
      "effect" : {
        "value" : local.kubernetes_prod.disable_privileged_containers_effect
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_kubernetes.outputs.kubernetes_allowed_kubernetes_version_id
  }

  # Kubernetes cluster should have 'Standard' SKU
  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_kubernetes.outputs.kubernetes_allowed_sku_id
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
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/0a15ec92-a229-4763-bb14-0ea34a568f8d"
    reference_id         = local.kubernetes_prod.enable_azure_policy_addon.reference_id
    parameter_values = jsonencode({
      "effect" : {
        "value" : local.kubernetes_prod.enable_azure_policy_addon.effect
      }
    })
  }
}

output "kubernetes_prod_id" {
  value = azurerm_policy_set_definition.kubernetes_prod.id
}
