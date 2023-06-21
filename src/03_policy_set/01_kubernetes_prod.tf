locals {
  kubernetes_prod = {
    metadata_category_name                  = "pagopa_prod"
    allowed_container_registry_reference_id = "allowed_container_registry"
    allowed_container_registry_effect       = "Audit"
    allowed_container_registry_regex        = "^([^\\/]+\\.azurecr\\.io|ghcr\\.io\\/pagopa|ghcr\\.io\\/kedacore|mcr\\.microsoft\\.com\\/azure-storage)\\/.+$"
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
          "${local.kubernetes_prod.allowed_container_registry_reference_id} : ${local.kubernetes_prod.allowed_container_registry_reference_id}": "${data.azurerm_management_group.pagopa.id}"
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
}

output "kubernetes_prod_id" {
  value = azurerm_policy_set_definition.kubernetes_prod.id
}
