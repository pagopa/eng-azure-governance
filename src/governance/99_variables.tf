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

#
# 💰 Budget
#
variable "budget_subscription" {
  type = object({
    amount     = number
    time_grain = string
    notifications = list(
      object({
        enabled        = bool
        threshold      = number
        operator       = string
        threshold_type = string
      })
    )
  })

  default     = null
  description = "Budgets rules for subscription"
}
