variable "subscription" {
  description = "The Subsription where this Policy Assignment should be created"
  type = object({
    id              = string
    subscription_id = string
    display_name    = string
  })
}

variable "location" {
  description = "The Azure Region where the Policy Assignment should exist"
  type        = string
}

variable "policy_set_ids" {
  description = "A map for each policy set id to assign"
  type        = map(string)
}

variable "metadata_category_name" {
  description = "Metadata category name"
  type        = string
  default     = "Custom PagoPA"
}

variable "audit_logs" {
  description = "Audit logs configuration"
  type        = map(string)
  default = {
    workspace_id                        = "novalue"
    storage_primary_region_storage_id   = "novalue"
    storage_primary_region_location     = "novalue"
    storage_secondary_region_storage_id = "novalue"
    storage_secondary_region_location   = "novalue"
  }
}

variable "metrics_logs" {
  description = "Metrics logs configuration"
  type        = map(string)
  default = {
    workspace_id = "novalue"
  }
}
