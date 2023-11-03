locals {
  storage_account_prod = {
    metadata_category_name = "pagopa_prod"
    allowed_sku = {
      reference_id = "allowed_sku_reference_id"
      effect       = "Audit"
      skus = [
        "Standard_ZRS",
        "Standard_GRS",
        "Standard_RAGRS",
        "Standard_GZRS",
        "Standard_RAGZRS",
        "Premium_ZRS",
      ]
    }
    secure_transfer = {
      reference_id = "secure_transfer_reference_id"
      effect       = "Deny"
    }
  }
}

resource "azurerm_policy_set_definition" "storage_account_prod" {
  name                = "storage_account_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Storage Account PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = local.storage_account_prod.metadata_category_name
    version  = "v1.0.0"
    ASC      = "true"
    parameterScopes = {
      "${local.storage_account_prod.allowed_sku.reference_id} : ${local.storage_account_prod.allowed_sku.reference_id}"         = data.azurerm_management_group.pagopa.id
      "${local.storage_account_prod.secure_transfer.reference_id} : ${local.storage_account_prod.secure_transfer.reference_id}" = data.azurerm_management_group.pagopa.id
    }
  })

  # Storage accounts should have the specified minimum TLS version (only TLS 1.2)
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/fe83a0eb-a853-422d-aac2-1bffd182c5d0"
    parameter_values     = jsonencode({})
  }

  # Secure transfer to storage accounts should be enabled
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/404c3081-a854-4457-ae30-26a93ef643f9"
    reference_id         = local.storage_account_prod.secure_transfer.reference_id
    parameter_values = jsonencode({
      effect = {
        value = local.storage_account_prod.secure_transfer.effect
      }
    })
  }

  # [Preview]: Storage account public access should be disallowed
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/4fa4b6c0-31ca-4c0d-b10d-24b96f62a751"
    parameter_values     = jsonencode({})
  }

  # Storage accounts should be limited by allowed SKUs
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/7433c107-6db4-4ad1-b57a-a76dce0154a1"
    reference_id         = local.storage_account_prod.allowed_sku.reference_id
    parameter_values = jsonencode({
      listOfAllowedSKUs = {
        value = local.storage_account_prod.allowed_sku.skus
      }
      effect = {
        value = local.storage_account_prod.allowed_sku.effect
      }
    })
  }
}

output "storage_account_prod_id" {
  value = azurerm_policy_set_definition.storage_account_prod.id
}
