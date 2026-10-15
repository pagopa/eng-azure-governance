locals {
  prod_pci_subscriptions = [
    "PROD-PCI",
  ]
}

module "prod_pci_assignments" {
  source = "./modules/prod_pci"

  for_each = toset(local.prod_pci_subscriptions)

  subscription   = [for s in data.azurerm_subscriptions.available.subscriptions : s if s.display_name == each.value][0]
  location       = var.location
  policy_set_ids = data.terraform_remote_state.policy_set.outputs

  audit_logs = {
    workspace_id                      = data.terraform_remote_state.policy_set.outputs.audit_logs_workspace_id
    storage_primary_region_storage_id = data.terraform_remote_state.policy_set.outputs.audit_logs_storage_id_westeurope
    storage_primary_region_location   = "westeurope"
    storage_secondary_region_location = "northeurope"
  }

  metrics_logs = {
    workspace_id = data.terraform_remote_state.policy_set.outputs.audit_logs_workspace_id
  }
}
