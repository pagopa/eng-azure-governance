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
