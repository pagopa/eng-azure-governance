locals {
  kubernetes_dev = {
    disable_privileged_containers = {
      reference_id        = "disable_privileged_containers_reference_id"
      effect              = "Audit"
      excluded_namespaces = ["kube-system", "gatekeeper-system", "azure-arc", "azure-extensions-usage-system", "elastic-system"]
    }
    disable_privilege_escalation = {
      reference_id        = "disable_privilege_escalation_reference_id"
      effect              = "Audit"
      excluded_namespaces = ["kube-system", "gatekeeper-system", "azure-arc", "azure-extensions-usage-system", "elastic-system"]
    }
    approved_user_group_ids = {
      reference_id        = "approved_user_group_ids_reference_id"
      effect              = "Audit"
      excluded_namespaces = ["kube-system", "gatekeeper-system", "azure-arc", "azure-extensions-usage-system", "elastic-system"]
    }
  }
}

resource "azurerm_policy_set_definition" "kubernetes_dev" {
  name                = "kubernetes_dev"
  policy_type         = "Custom"
  display_name        = "PagoPA Kubernetes DEV"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = "pagopa_dev"
    version  = "v1.0.0"
    ASC      = "true"
    parameterScopes = {
      for _, param in local.kubernetes_dev : "${param.reference_id} : ${param.reference_id}" => data.azurerm_management_group.pagopa.id
    }
  })

  # Kubernetes cluster should not allow privileged containers
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/95edb821-ddaf-4404-9732-666045e056b4"
    reference_id         = local.kubernetes_dev.disable_privileged_containers.reference_id
    parameter_values = jsonencode({
      effect = {
        value = local.kubernetes_dev.disable_privileged_containers.effect
      }
      excludedNamespaces = {
        value = local.kubernetes_dev.disable_privileged_containers.excluded_namespaces
      }
    })
  }

  # Kubernetes clusters should not allow container privilege escalation
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/1c6e92c9-99f0-4e55-9cf2-0c234dc48f99"
    reference_id         = local.kubernetes_dev.disable_privilege_escalation.reference_id
    parameter_values = jsonencode({
      effect = {
        value = local.kubernetes_dev.disable_privilege_escalation.effect
      }
      excludedNamespaces = {
        value = local.kubernetes_dev.disable_privilege_escalation.excluded_namespaces
      }
    })
  }

  # Kubernetes cluster containers should run with approved user and group IDs
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/f06ddb64-5fa3-4b77-b166-acb36f7f6042"
    reference_id         = local.kubernetes_dev.approved_user_group_ids.reference_id
    parameter_values = jsonencode({
      effect = {
        value = local.kubernetes_dev.approved_user_group_ids.effect
      }
      excludedNamespaces = {
        value = local.kubernetes_dev.approved_user_group_ids.excluded_namespaces
      }
    })
  }
}
