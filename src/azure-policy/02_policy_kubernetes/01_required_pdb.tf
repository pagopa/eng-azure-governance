resource "azurerm_policy_definition" "kubernetes_required_pdb" {
  name                = "kubernetes_required_pdb"
  policy_type         = "Custom"
  mode                = "Microsoft.Kubernetes.Data"
  display_name        = "PagoPA Kubernetes required PDB"
  description         = "Kubernetes Deployments and StatefulSets with at least minReplicas replicas must be covered by a PodDisruptionBudget whose matchLabels select the pod template labels."
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Kubernetes Deployments and StatefulSets with at least minReplicas replicas should be covered by a PodDisruptionBudget"
      Severity               = "Medium"
    }
  })

  parameters = file("./policy_rules/required_pdb_parameters.json")

  policy_rule = templatefile("./policy_rules/required_pdb_policy.json", { templateInfoContent = filebase64("./policy_rules/required_pdb_gatekeeper.yaml") })
}
