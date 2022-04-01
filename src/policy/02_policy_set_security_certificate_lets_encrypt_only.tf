resource "azurerm_policy_set_definition" "security_certificate_lets_encrypt_only" {
  name                = "pagopa_security_certificate_lets_encrypt_only"
  policy_type         = "Custom"
  display_name        = "PagoPA policy to discover certificates that don't use let's encrypt as CA"
  management_group_id = data.azurerm_management_group.prod_sl_pagamenti_servizi.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
METADATA

  parameters = <<PARAMETERS
  {
    "caCommonName": {
      "type": "String",
      "metadata": {
        "displayName": "The common name of the certificate authority",
        "description": "The common name (CN) of the Certificate Authority (CA) provider. For example, for an issuer CN = Contoso, OU = .., DC = .., you can specify Contoso"
      }
    }
  }
PARAMETERS

  # Certificates should be issued by the specified non-integrated certificate authority
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/a22f4a40-01d3-4c7d-8071-da157eeff341"
    parameter_values     = <<VALUE
    {
      "caCommonName": {
        "value": "[parameters('caCommonName')]"
      }
    }
    VALUE
  }
}

#
# Asingment
#

locals {
  cn_name = jsonencode(var.certificate_authority_cn)
}

resource "azurerm_management_group_policy_assignment" "security_certificate_lets_encrypt_only_2_root_sl_pay" {
  name                 = "pacertletsencr2root"
  display_name         = "PagoPA/SEC/PROD/ADVICE to discover certificates that don't use let's encrypt as CA"
  policy_definition_id = azurerm_policy_set_definition.security_certificate_lets_encrypt_only.id
  management_group_id  = data.azurerm_management_group.prod_sl_pagamenti_servizi.id

  location = var.location
  enforce  = false

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA

  parameters = <<PARAMS
  {
      "caCommonName": {
          "value": ${local.cn_name}
      }
  }
  PARAMS

  identity {
    type = "SystemAssigned"
  }
}
