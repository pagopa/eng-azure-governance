# Enforced
resource "azurerm_policy_set_definition" "security_tls_1_2" {
  name                  = "pagopa_security_tls_1_2"
  policy_type           = "Custom"
  display_name          = "PagoPA policy resources must use TLS 1.2"
  management_group_id = data.azurerm_management_group.prod_sl_pagamenti_servizi.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA

  # Azure SQL Database should be running TLS version 1.2 or newer
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/32e6bbec-16b6-44c2-be37-c5b672d103cf"
  }

  # App Service Environment should disable TLS 1.0 and 1.1
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/d6545c6b-dd9d-4265-91e6-0b451e2f1c50"
  }

  # Latest TLS version should be used in your Function App
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/f9d614c5-c173-4d56-95a7-b4437057d193"
  }

  # Latest TLS version should be used in your Web App
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/f0e6e85b-9b9f-4a4b-b67b-f730d42f1b0b"
  }

} # end

#
# Asingment
#

resource "azurerm_management_group_policy_assignment" "security_tls_1_2" {
  name                 = "patls12conn2root"
  display_name         = "PagoPA/SEC/PROD/ADVICE policy resources must use TLS 1.2 "
  policy_definition_id = azurerm_policy_set_definition.security_tls_1_2.id
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
