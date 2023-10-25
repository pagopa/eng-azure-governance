locals {
  tags = {
    CostCenter = {
      required = true
      allowed_values = [
        "TS000 - TECNOLOGIA & SERVIZI",
        "TS100 - TECNOLOGIA",
        "TS110 - SVILUPPO E ARCHITETTURA",
        "TS120 - CLIENT E FRONTEND",
        "TS200 - SICUREZZA",
        "TS300 - PRODOTTI E SERVIZI",
        "TS310 - PAGAMENTI & SERVIZI",
        "TS320 - PIATTAFORMA NOTIFICHE DIGITALI",
        "TS330 - PDND & INTEROPERABILITA'"
      ]
    }
    Owner = {
      required       = true
      allowed_values = []
    }
    Environment = {
      required       = true
      allowed_values = ["Dev", "Prod", "Uat"]
    }
    CreatedBy = {
      required       = false
      allowed_values = ["terraform", "aws cli", "arm", "cloud formation"]
    }
    Backup = {
      required       = false
      allowed_values = ["Yes", "No"]
    }
    DisasterRecovery = {
      required       = false
      allowed_values = ["MultiAz", "MultiRegion"]
    }
  }
}

resource "azurerm_policy_set_definition" "tags" {
  name                = "tags"
  policy_type         = "Custom"
  display_name        = "PagoPA Tags"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "pagopa_prod",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  dynamic "policy_definition_group" {
    for_each = [for name, tag in local.tags : name]

    content {
      name = policy_definition_group.value
    }
  }

  dynamic "policy_definition_reference" {
    for_each = [for name, tag in local.tags : name if tag.required]

    content {
      policy_definition_id = data.terraform_remote_state.policy_tags.outputs.tags_require_tag_id
      policy_group_names   = [policy_definition_reference.value]
      parameter_values     = <<VALUE
      {
        "tagName": {
          "value": "${policy_definition_reference.value}"
        }
      }
      VALUE
    }
  }

  dynamic "policy_definition_reference" {
    for_each = [for name, tag in local.tags : name if length(tag.allowed_values) > 0]

    content {
      policy_definition_id = data.terraform_remote_state.policy_tags.outputs.tags_require_tag_values_id
      policy_group_names   = [policy_definition_reference.value]
      parameter_values     = <<VALUE
      {
        "tagName": {
          "value": "${policy_definition_reference.value}"
        },
        "tagValues": {
          "value": ${jsonencode(local.tags[policy_definition_reference.value].allowed_values)}
        }
      }
      VALUE
    }
  }
}

output "tags_id" {
  value = azurerm_policy_set_definition.tags.id
}
