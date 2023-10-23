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
      required = true
    }
    Environment = {
      required = true
      allowed_values = ["Dev", "Prod", "Uat"]
    }
    CreatedBy = {
      required = false
      allowed_values = ["terraform", "aws cli", "arm", "cloud formation", "email?"]
    }
    Backup = {
      required = false
      allowed_values = ["Si", "No"]
    }
    DisasterRecovery = {
      required = false
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

  dynamic "policy_definition_reference" {
    for_each = [for name, tag in local.tags : name if tag.required ]

    content {
      policy_definition_id = data.terraform_remote_state.policy_tags.outputs.tags_require_tag_id
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
    for_each = [for name, tag in local.tags : name => tag if tag.allowed_values]

    content {
      policy_definition_id = data.terraform_remote_state.policy_tags.outputs.tags_require_tag_values_id
      parameter_values     = <<VALUE
      {
        "tagName": {
          "value": "${policy_definition_reference.key}"
        },
        "tagValues": {
          "value": ${policy_definition_reference.value.allowed_values}
        }
      }
      VALUE
    }
  }
}
