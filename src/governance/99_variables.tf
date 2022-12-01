variable "prefix" {
  type        = string
  description = "Project prefix"
}

variable "env" {
  type        = string
  default     = ""
  description = "Environment name"
}

variable "env_short" {
  type        = string
  description = "(Required)"
}

variable "location" {
  type        = string
  description = "(Required) Region choosed to deploy the resources"
  default     = "West Europe"
}

variable "location_short" {
  type        = string
  default     = "weu"
  description = "Short location form to avoid names to much larger"

  validation {
    condition     = contains(["weu", "neu", "eus2"], var.location_short)
    error_message = "Allowed values for location_short are \"weu\", \"neu\", or \"eus2\"."
  }
}

variable "subscription_foundation" {
  type        = bool
  default     = false
  description = "Allows you to enable the creation of vault, AD permissions and other configurations for the subscription if not present"
}

variable "tags_subscription" {
  type        = map(any)
  default     = {}
  description = "Tags that will be used by subscriptions"
}

#
# 💰 Budget
#
variable "budget_subscription_enabled" {
  type        = bool
  description = "Enabled or not budget for this subscription"
  default     = false
}
variable "budget_subscription_resource_group" {
  type        = string
  description = "Resource group where the monitoring is saved"
  default     = "MOCK_VALUE"
}

variable "action_group_budget_resource_group" {
  type        = string
  description = "Action group resource group"
  default     = "MOCK_VALUE"
}

variable "action_group_budget_name" {
  type        = string
  description = "Action group for Budget name"
  default     = "MOCK_VALUE"
}

variable "budget_subscription_time_grain" {
  type        = string
  description = "(Required) The time covered by a budget. Tracking of the amount will be reset based on the time grain. Must be one of BillingAnnual, BillingMonth, BillingQuarter, Annually, Monthly and Quarterly. Defaults to Monthly."
  default     = "MOCK_VALUE"
}

variable "budget_subscription_amount" {
  type        = string
  description = "(Required) The total amount of cost to track with the budget."
  default     = "0"
}

variable "budget_subscription_notifications" {
  type = list(
    object({
      enabled        = bool   # (Optional) Should the notification be enabled?
      threshold      = number #(Required) Threshold value associated with a notification. Notification is sent when the cost exceeded the threshold. It is always percent and has to be between 0 and 1000.
      operator       = string # (Required) The comparison operator for the notification. Must be one of EqualTo, GreaterThan, or GreaterThanOrEqualTo.
      threshold_type = string # (Optional) The type of threshold for the notification. This determines whether the notification is triggered by forecasted costs or actual costs. The allowed values are Actual and Forecasted. Default is Actual.
    })
  )
  description = "Notification configuration for every budget"
  default = [{
    enabled        = false
    operator       = "value"
    threshold      = 1
    threshold_type = "value"
  }]
}
