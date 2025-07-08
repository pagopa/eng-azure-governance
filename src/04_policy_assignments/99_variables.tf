variable "metadata_category_name" {
  type        = string
  description = "metadata category name"
  default     = "Custom PagoPA"
}

variable "policy_type" {
  type        = string
  description = "policy type"
  default     = "Custom"
}

variable "location" {
  type        = string
  description = "location"
  default     = "westeurope"
}

variable "subscription_id" {
  description = "The Azure subscription ID to use"
  type        = string
}