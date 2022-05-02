# Advices
resource "azurerm_policy_set_definition" "prod_set_advice" {
  name                = "pagopa_prod_set_advice"
  policy_type         = "Custom"
  display_name        = "PagoPA/PROD/set/advice@prod management group"
  management_group_id = data.azurerm_management_group.prod_sl_pagamenti_servizi.group_id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA

  parameters = <<PARAMETERS
  {
    "listOfAllowedSKUs": {
      "type": "Array",
      "metadata": {
        "description": "The list of size SKUs that can be specified for virtual machines.",
        "displayName": "Allowed Size SKUs",
        "strongType": "VMSKUs"
      },
      "defaultValue" : [""]
    }
  }
  PARAMETERS

  # allowed skus
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/cccc23c7-8427-4f53-ad12-b6a63eb452b3"
    parameter_values     = <<VALUE
    {
      "listOfAllowedSKUs": {
        "value": "[parameters('listOfAllowedSKUs')]"
      }
    }
    VALUE
  }

  # Web Application Firewall (WAF) should be enabled for Application Gateway
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/564feb30-bf6a-4854-b4bb-0d2d2d1e6c66"
  }

#
# HTTPS Only
#

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

#
# Not public endpoint
#
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

  # API Management services should disable public network access
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/df73bd95-24da-4a4f-96b9-4e8b94b402bd"
  }

#
# TLS >= 1.2
#
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
}

#
# Asingment
#

locals {
  list_allow_skus_raw_prod    = jsonencode(var.prod_vm_skus_allowed)
}

resource "azurerm_management_group_policy_assignment" "prod_set_advice_2_root_sl_pay" {
  name                 = "pa_prodsetadv2rootslpay"
  display_name         = "PagoPA/PROD/SET/ADVICE 2 Mgmt root sl servizi e pagamenti"
  policy_definition_id = azurerm_policy_set_definition.prod_set_advice.id
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
      "listOfAllowedSKUs": {
          "value": ${local.list_allow_skus_raw_prod}
      }
  }
  PARAMS

  identity {
    type = "SystemAssigned"
  }
}
