locals {
  uat_pci_subscriptions = [
    "UAT-PCI",
  ]
}

module "uat_pci_assignments" {
  source = "./modules/uat_pci"

  for_each = toset(local.uat_pci_subscriptions)

  subscription   = [for s in data.azurerm_subscriptions.available.subscriptions : s if s.display_name == each.value][0]
  location       = var.location
  policy_set_ids = data.terraform_remote_state.policy_set.outputs

  audit_logs = {
    workspace_id                        = "/subscriptions/94004462-d636-48bc-aa63-ce22a99d6bf2/resourcegroups/pci-d-weu-core-monitor-rg/providers/microsoft.operationalinsights/workspaces/pci-d-weu-core-law"
    storage_primary_region_storage_id   = "/subscriptions/ac17914c-79bf-48fa-831e-1359ef74c1d5/resourcegroups/devopslab-logs/providers/Microsoft.Storage/storageAccounts/devopslablogs"
    storage_secondary_region_storage_id = "novalue"
    storage_primary_region_location     = "westeurope"
    storage_secondary_region_location   = "northeurope"
  }

  metrics_logs = {
    workspace_id = "/subscriptions/94004462-d636-48bc-aa63-ce22a99d6bf2/resourcegroups/pci-d-weu-core-monitor-rg/providers/microsoft.operationalinsights/workspaces/pci-d-weu-core-law"
  }
}
