resource "azurerm_policy_set_definition" "security_https_only" {
  name                  = "pagopa_security_https_only"
  policy_type           = "Custom"
  display_name          = "PagoPA policy not allow public endpoint for storage or internal resources"
  management_group_name = data.azurerm_management_group.prod_sl_pagamenti_servizi.name

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA

  # Web Application should only be accessible over HTTPS
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/a4af4a39-4135-47fb-b175-47fbdf85311d"
  }

  # Function App should only be accessible over HTTPS
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/6d555dd1-86f2-4f1c-8ed7-5abae7c6cbab"
  }

  # Azure Kubernetes Service Private Clusters should be enabled
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/040732e8-d947-40b8-95d6-854c95024bf8"
  }

  # Kubernetes clusters should be accessible only over HTTPS
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/1a5b4dca-0b6f-4cf5-907c-56316bc1bf3d"
  }

} # end

#
# Asingment
#

resource "azurerm_management_group_policy_assignment" "security_https_only" {
  name                 = "pagohttpsonlyadv2root"
  display_name         = "PagoPA/SEC/PROD/ADVICE policy allow only https communication"
  policy_definition_id = azurerm_policy_set_definition.security_https_only.id
  management_group_id  = data.azurerm_management_group.prod_sl_pagamenti_servizi.id

  location = var.location
  enforce  = false

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
METADATA

  identity {
    type = "SystemAssigned"
  }
}
