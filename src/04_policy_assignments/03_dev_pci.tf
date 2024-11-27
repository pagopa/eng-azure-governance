locals {
  dev_pci_subscriptions = [
    "DEV-PCI",
  ]
}

module "dev_pci_assignments" {
  source = "./modules/dev_pci"

  for_each = toset(local.dev_pci_subscriptions)

  subscription   = [for s in data.azurerm_subscriptions.available.subscriptions : s if s.display_name == each.value][0]
  location       = var.location
  policy_set_ids = data.terraform_remote_state.policy_set.outputs

  metrics_logs = {
    workspace_id = "/subscriptions/94004462-d636-48bc-aa63-ce22a99d6bf2/resourcegroups/pci-d-weu-core-monitor-rg/providers/microsoft.operationalinsights/workspaces/pci-d-weu-core-law"
  }
}
