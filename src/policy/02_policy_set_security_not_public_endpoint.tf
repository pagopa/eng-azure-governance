resource "azurerm_policy_set_definition" "security_no_public_endpoint" {
  name                  = "pagopa_security_no_public_endpoint"
  policy_type           = "Custom"
  display_name          = "PagoPA policy not allow public endpoint for storage or internal resources"
  management_group_name = data.azurerm_management_group.prod_sl_pagamenti_servizi.name

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA

  # Public network access should be disabled for Container registries
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/0fdf0491-d080-4575-b627-ad0e843cba0f"
  }

  # Azure Cosmos DB should disable public network access
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/797b37f7-06b8-444c-b1ad-fc62867f335a"
  }

  # Azure Cache for Redis should disable public network access
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/470baccb-7e51-4549-8b1a-3e5be069f663"
  }

  # Public network access should be disabled for PostgreSQL servers
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/b52376f7-9612-48a1-81cd-1ffe4b61032c"
  }

  # [Preview]: Azure Key Vault should disable public network access
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/55615ac9-af46-4a59-874e-391cc3dfb490"
  }

  # App Services should disable public network access
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/63a0ac64-5d5f-4569-8a3d-df67cc1ce9d7"
  }

} # end

#
# Asingment
#

resource "azurerm_management_group_policy_assignment" "security_no_public_endpoint" {
  name                 = "panopubconnadv2root"
  display_name         = "PagoPA/SEC/PROD/ADVICE policy not allow public endpoint for storage or internal resources"
  policy_definition_id = azurerm_policy_set_definition.security_no_public_endpoint.id
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
