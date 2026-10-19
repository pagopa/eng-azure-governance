mock_provider "azurerm" {
  mock_data "azurerm_management_group" {
    defaults = {
      id   = "/providers/Microsoft.Management/managementGroups/pagopa"
      name = "pagopa"
    }
  }
}

variables {
  subscription_id = "00000000-0000-0000-0000-000000000000"
}

run "required_pdb_definition_identity" {
  command = plan

  assert {
    condition     = azurerm_policy_definition.kubernetes_required_pdb.name == "kubernetes_required_pdb"
    error_message = "Custom required PDB definition must be named kubernetes_required_pdb."
  }

  assert {
    condition     = azurerm_policy_definition.kubernetes_required_pdb.mode == "Microsoft.Kubernetes.Data"
    error_message = "Custom required PDB definition must use mode Microsoft.Kubernetes.Data."
  }

  assert {
    condition     = azurerm_policy_definition.kubernetes_required_pdb.policy_type == "Custom"
    error_message = "Custom required PDB definition must be of policy_type Custom."
  }

  assert {
    condition     = azurerm_policy_definition.kubernetes_required_pdb.display_name == "PagoPA Kubernetes required PDB"
    error_message = "Custom required PDB display name is not the expected value."
  }
}

run "required_pdb_parameters_contract" {
  command = plan

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.parameters).effect.defaultValue == "Audit"
    error_message = "effect must default to Audit."
  }

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.parameters).effect.allowedValues == ["Audit", "Deny", "Disabled"]
    error_message = "effect allowedValues must be Audit, Deny and Disabled."
  }

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.parameters).effect.type == "String"
    error_message = "effect must be of type String."
  }

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.parameters).minReplicas.type == "Integer"
    error_message = "minReplicas must be of type Integer."
  }

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.parameters).minReplicas.defaultValue == 3
    error_message = "minReplicas must default to 3."
  }

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.parameters).namespaces.type == "Array"
    error_message = "namespaces must be of type Array."
  }

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.parameters).excludedNamespaces.type == "Array"
    error_message = "excludedNamespaces must be of type Array."
  }

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.parameters).labelSelector.type == "Object"
    error_message = "labelSelector must be of type Object."
  }
}

run "required_pdb_policy_rule_forwarding" {
  command = plan

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.policy_rule).then.effect == "[parameters('effect')]"
    error_message = "policy_rule effect must be forwarded from the effect parameter."
  }

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.policy_rule).then.details.apiGroups == ["apps"]
    error_message = "policy_rule apiGroups must be [\"apps\"]."
  }

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.policy_rule).then.details.kinds == ["Deployment", "StatefulSet"]
    error_message = "policy_rule kinds must be Deployment and StatefulSet."
  }

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.policy_rule).then.details.values.minReplicas == "[parameters('minReplicas')]"
    error_message = "policy_rule must forward details.values.minReplicas from the minReplicas parameter."
  }

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.policy_rule).then.details.namespaces == "[parameters('namespaces')]"
    error_message = "policy_rule must forward namespaces."
  }

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.policy_rule).then.details.excludedNamespaces == "[parameters('excludedNamespaces')]"
    error_message = "policy_rule must forward excludedNamespaces."
  }

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.policy_rule).then.details.labelSelector == "[parameters('labelSelector')]"
    error_message = "policy_rule must forward labelSelector."
  }

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.policy_rule).then.details.templateInfo.sourceType == "Base64Encoded"
    error_message = "policy_rule templateInfo sourceType must be Base64Encoded."
  }

  assert {
    condition     = jsondecode(azurerm_policy_definition.kubernetes_required_pdb.policy_rule).then.details.templateInfo.content == filebase64("./policy_rules/required_pdb_gatekeeper.yaml")
    error_message = "policy_rule template content must equal the Base64 of the distributed ConstraintTemplate file."
  }
}
