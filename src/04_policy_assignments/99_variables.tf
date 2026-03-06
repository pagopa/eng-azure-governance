variable "metadata_category_name" {
  type        = string
  description = "metadata category name"
}

variable "policy_type" {
  type        = string
  description = "policy type"
}

variable "location" {
  type        = string
  description = "location"
}

variable "subscription_id" {
  description = "The Azure subscription ID to use"
  type        = string
}

variable "subscriptions_by_env" {
  description = "Subscription display names grouped by environment"
  type = object({
    dev  = list(string)
    uat  = list(string)
    prod = list(string)
  })
}
