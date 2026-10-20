mock_provider "azurerm" {
  mock_data "azurerm_management_group" {
    defaults = {
      id   = "/providers/Microsoft.Management/managementGroups/pagopa"
      name = "pagopa"
    }
  }

  mock_data "azurerm_policy_definition" {
    defaults = {
      id = "/providers/Microsoft.Authorization/policyDefinitions/00000000-0000-0000-0000-000000000000"
    }
  }
}

variables {
  subscription_id = "00000000-0000-0000-0000-000000000000"
}

run "kubernetes_dev_identity_and_builtins" {
  command = plan

  assert {
    condition     = azurerm_policy_set_definition.kubernetes_dev.name == "kubernetes_dev"
    error_message = "DEV Kubernetes set must be named kubernetes_dev."
  }

  assert {
    condition     = azurerm_policy_set_definition.kubernetes_dev.display_name == "PagoPA Kubernetes DEV"
    error_message = "DEV Kubernetes set display name is not the expected value."
  }

  assert {
    condition     = jsondecode(azurerm_policy_set_definition.kubernetes_dev.metadata).category == "pagopa_dev"
    error_message = "DEV Kubernetes set category must be pagopa_dev."
  }

  assert {
    condition     = length(azurerm_policy_set_definition.kubernetes_dev.policy_definition_reference) == 3
    error_message = "DEV Kubernetes set must contain exactly three references."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_dev.policy_definition_reference : r if r.policy_definition_id == "/providers/Microsoft.Authorization/policyDefinitions/95edb821-ddaf-4404-9732-666045e056b4"][0].parameter_values).effect.value == "Audit"
    error_message = "DEV privileged containers reference must set effect Audit explicitly."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_dev.policy_definition_reference : r if r.policy_definition_id == "/providers/Microsoft.Authorization/policyDefinitions/1c6e92c9-99f0-4e55-9cf2-0c234dc48f99"][0].parameter_values).effect.value == "Audit"
    error_message = "DEV privilege escalation reference must set effect Audit explicitly."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_dev.policy_definition_reference : r if r.policy_definition_id == "/providers/Microsoft.Authorization/policyDefinitions/f06ddb64-5fa3-4b77-b166-acb36f7f6042"][0].parameter_values).effect.value == "Audit"
    error_message = "DEV approved user/group IDs reference must set effect Audit explicitly."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_dev.policy_definition_reference : r if r.policy_definition_id == "/providers/Microsoft.Authorization/policyDefinitions/95edb821-ddaf-4404-9732-666045e056b4"][0].parameter_values).excludedNamespaces.value == ["kube-system", "gatekeeper-system", "azure-arc", "azure-extensions-usage-system", "elastic-system"]
    error_message = "DEV privileged containers reference must exclude the common namespaces."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_dev.policy_definition_reference : r if r.policy_definition_id == "/providers/Microsoft.Authorization/policyDefinitions/1c6e92c9-99f0-4e55-9cf2-0c234dc48f99"][0].parameter_values).excludedNamespaces.value == ["kube-system", "gatekeeper-system", "azure-arc", "azure-extensions-usage-system", "elastic-system"]
    error_message = "DEV privilege escalation reference must exclude the common namespaces."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_dev.policy_definition_reference : r if r.policy_definition_id == "/providers/Microsoft.Authorization/policyDefinitions/f06ddb64-5fa3-4b77-b166-acb36f7f6042"][0].parameter_values).excludedNamespaces.value == ["kube-system", "gatekeeper-system", "azure-arc", "azure-extensions-usage-system", "elastic-system"]
    error_message = "DEV approved user/group IDs reference must exclude the common namespaces."
  }

  assert {
    condition     = length([for r in azurerm_policy_set_definition.kubernetes_dev.policy_definition_reference : r if endswith(r.policy_definition_id, "d9e8f2c1-4c5a-4f5c-8b5a-2abf1e9f7b4d")]) == 0
    error_message = "DEV set must not contain the accurate PDB built-in."
  }
}

run "kubernetes_uat_identity_and_builtins" {
  command = plan

  assert {
    condition     = azurerm_policy_set_definition.kubernetes_uat.name == "kubernetes_uat"
    error_message = "UAT Kubernetes set must be named kubernetes_uat."
  }

  assert {
    condition     = azurerm_policy_set_definition.kubernetes_uat.display_name == "PagoPA Kubernetes UAT"
    error_message = "UAT Kubernetes set display name is not the expected value."
  }

  assert {
    condition     = jsondecode(azurerm_policy_set_definition.kubernetes_uat.metadata).category == "pagopa_uat"
    error_message = "UAT Kubernetes set category must be pagopa_uat."
  }

  assert {
    condition     = length(azurerm_policy_set_definition.kubernetes_uat.policy_definition_reference) == 3
    error_message = "UAT Kubernetes set must contain exactly three references."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_uat.policy_definition_reference : r if r.policy_definition_id == "/providers/Microsoft.Authorization/policyDefinitions/95edb821-ddaf-4404-9732-666045e056b4"][0].parameter_values).effect.value == "Audit"
    error_message = "UAT privileged containers reference must set effect Audit explicitly."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_uat.policy_definition_reference : r if r.policy_definition_id == "/providers/Microsoft.Authorization/policyDefinitions/1c6e92c9-99f0-4e55-9cf2-0c234dc48f99"][0].parameter_values).effect.value == "Audit"
    error_message = "UAT privilege escalation reference must set effect Audit explicitly."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_uat.policy_definition_reference : r if r.policy_definition_id == "/providers/Microsoft.Authorization/policyDefinitions/f06ddb64-5fa3-4b77-b166-acb36f7f6042"][0].parameter_values).effect.value == "Audit"
    error_message = "UAT approved user/group IDs reference must set effect Audit explicitly."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_uat.policy_definition_reference : r if r.policy_definition_id == "/providers/Microsoft.Authorization/policyDefinitions/f06ddb64-5fa3-4b77-b166-acb36f7f6042"][0].parameter_values).excludedNamespaces.value == ["kube-system", "gatekeeper-system", "azure-arc", "azure-extensions-usage-system", "elastic-system"]
    error_message = "UAT approved user/group IDs reference must exclude the common namespaces."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_uat.policy_definition_reference : r if r.policy_definition_id == "/providers/Microsoft.Authorization/policyDefinitions/95edb821-ddaf-4404-9732-666045e056b4"][0].parameter_values).excludedNamespaces.value == ["kube-system", "gatekeeper-system", "azure-arc", "azure-extensions-usage-system", "elastic-system"]
    error_message = "UAT privileged containers reference must exclude the common namespaces."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_uat.policy_definition_reference : r if r.policy_definition_id == "/providers/Microsoft.Authorization/policyDefinitions/1c6e92c9-99f0-4e55-9cf2-0c234dc48f99"][0].parameter_values).excludedNamespaces.value == ["kube-system", "gatekeeper-system", "azure-arc", "azure-extensions-usage-system", "elastic-system"]
    error_message = "UAT privilege escalation reference must exclude the common namespaces."
  }

  assert {
    condition     = length([for r in azurerm_policy_set_definition.kubernetes_uat.policy_definition_reference : r if endswith(r.policy_definition_id, "d9e8f2c1-4c5a-4f5c-8b5a-2abf1e9f7b4d")]) == 0
    error_message = "UAT set must not contain the accurate PDB built-in."
  }
}

run "kubernetes_prod_new_references" {
  command = apply

  override_data {
    target = data.azurerm_policy_definition.this["kubernetes_required_pdb"]
    values = {
      id = "/providers/Microsoft.Authorization/policyDefinitions/11111111-1111-1111-1111-111111111111"
    }
  }

  assert {
    condition     = length(azurerm_policy_set_definition.kubernetes_prod.policy_definition_reference) == 13
    error_message = "PROD Kubernetes set must contain the 11 existing references plus the two PDB references."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_prod.policy_definition_reference : r if r.reference_id == "accurate_pdb_reference_id"][0].parameter_values).effect.value == "Audit"
    error_message = "PROD accurate PDB reference must set effect Audit."
  }

  assert {
    condition     = endswith([for r in azurerm_policy_set_definition.kubernetes_prod.policy_definition_reference : r if r.reference_id == "accurate_pdb_reference_id"][0].policy_definition_id, "d9e8f2c1-4c5a-4f5c-8b5a-2abf1e9f7b4d")
    error_message = "PROD accurate PDB reference must point to built-in d9e8f2c1-4c5a-4f5c-8b5a-2abf1e9f7b4d."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_prod.policy_definition_reference : r if r.reference_id == "accurate_pdb_reference_id"][0].parameter_values).excludedNamespaces.value == ["kube-system", "gatekeeper-system", "azure-arc", "azure-extensions-usage-system", "elastic-system"]
    error_message = "PROD accurate PDB reference must exclude the common namespaces."
  }

  assert {
    condition     = [for r in azurerm_policy_set_definition.kubernetes_prod.policy_definition_reference : r if r.reference_id == "required_pdb_reference_id"][0].policy_definition_id == data.azurerm_policy_definition.this["kubernetes_required_pdb"].id
    error_message = "PROD required PDB reference must resolve through the kubernetes_required_pdb data source."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_prod.policy_definition_reference : r if r.reference_id == "required_pdb_reference_id"][0].parameter_values).effect.value == "Audit"
    error_message = "PROD required PDB reference must set effect Audit."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_prod.policy_definition_reference : r if r.reference_id == "required_pdb_reference_id"][0].parameter_values).minReplicas.value == 3
    error_message = "PROD required PDB reference must set minReplicas to 3."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_prod.policy_definition_reference : r if r.reference_id == "required_pdb_reference_id"][0].parameter_values).excludedNamespaces.value == ["kube-system", "gatekeeper-system", "azure-arc", "azure-extensions-usage-system", "elastic-system"]
    error_message = "PROD required PDB reference must exclude the common namespaces."
  }

  assert {
    condition     = jsondecode([for r in azurerm_policy_set_definition.kubernetes_prod.policy_definition_reference : r if r.reference_id == "disable_privileged_containers_reference_id"][0].parameter_values).effect.value == "Deny"
    error_message = "Existing PROD privileged containers effect must remain Deny."
  }

  assert {
    condition     = length([for r in azurerm_policy_set_definition.kubernetes_prod.policy_definition_reference : r if r.reference_id == "allowed_container_registry"]) == 1
    error_message = "Existing PROD allowed container registry reference must be preserved."
  }

  assert {
    condition = {
      for r in azurerm_policy_set_definition.kubernetes_prod.policy_definition_reference : r.reference_id => jsondecode(r.parameter_values).effect.value
      if try(jsondecode(r.parameter_values).effect.value, null) != null
      } == {
      allowed_container_registry                        = "Audit"
      disable_privileged_containers_reference_id        = "Deny"
      disable_privilege_escalation_reference_id         = "Audit"
      disable_capsysadmin_reference_id                  = "Deny"
      enable_azure_policy_addon_reference_id            = "Deny"
      enable_defender_profile_reference_id              = "Deny"
      disable_api_credentials_automounting_reference_id = "Audit"
      enforce_apparmor_profile_reference_id             = "Deny"
      accurate_pdb_reference_id                         = "Audit"
      required_pdb_reference_id                         = "Audit"
    }
    error_message = "PROD reference effects must match the characterized baseline plus the two new PDB references."
  }

  assert {
    condition = alltrue([
      for k, v in {
        allowed_container_registry                        = "/providers/Microsoft.Authorization/policyDefinitions/febd0533-8e55-448f-b837-bd0e06f16469"
        disable_privileged_containers_reference_id        = "/providers/Microsoft.Authorization/policyDefinitions/95edb821-ddaf-4404-9732-666045e056b4"
        disable_privilege_escalation_reference_id         = "/providers/Microsoft.Authorization/policyDefinitions/1c6e92c9-99f0-4e55-9cf2-0c234dc48f99"
        disable_capsysadmin_reference_id                  = "/providers/Microsoft.Authorization/policyDefinitions/d2e7ea85-6b44-4317-a0be-1b951587f626"
        disable_api_credentials_automounting_reference_id = "/providers/Microsoft.Authorization/policyDefinitions/423dd1ba-798e-40e4-9c4d-b6902674b423"
        enforce_apparmor_profile_reference_id             = "/providers/Microsoft.Authorization/policyDefinitions/511f5417-5d12-434d-ab2e-816901e72a5e"
        accurate_pdb_reference_id                         = "/providers/Microsoft.Authorization/policyDefinitions/d9e8f2c1-4c5a-4f5c-8b5a-2abf1e9f7b4d"
        required_pdb_reference_id                         = "/providers/Microsoft.Authorization/policyDefinitions/11111111-1111-1111-1111-111111111111"
        } : {
        for r in azurerm_policy_set_definition.kubernetes_prod.policy_definition_reference : r.reference_id => r.policy_definition_id
        if r.reference_id != null
      }[k] == v
    ])
    error_message = "PROD literal references must keep their built-in IDs, and required_pdb must resolve to the overridden custom definition ID (proves the data-source key)."
  }
}
