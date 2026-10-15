variable "metadata_category_name" {
  type        = string
  description = "metadata category name"
}

variable "location" {
  type        = string
  description = "location"
}

variable "subscription_id" {
  description = "The Azure subscription ID to use"
  type        = string
}

variable "subscription_blacklist" {
  description = "Subscription display names or subscription UUIDs excluded from environment assignments, matched case-insensitively"
  type        = set(string)
  default     = []
  nullable    = false

  validation {
    condition     = alltrue([for entry in var.subscription_blacklist : try(trimspace(entry) != "", false)])
    error_message = "Blacklist entries must be non-empty subscription display names or subscription UUIDs."
  }
}

variable "subscription_environment_overrides" {
  description = "Environment overrides keyed by subscription display name or UUID; UUID overrides take precedence over names and prefixes"
  type        = map(string)
  default     = {}
  nullable    = false

  validation {
    condition = alltrue([
      for subscription, environment in var.subscription_environment_overrides :
      trimspace(subscription) != "" && contains(["dev", "uat", "prod"], environment)
    ])
    error_message = "Override keys must be non-empty names or UUIDs, and environments must be dev, uat, or prod."
  }

  validation {
    condition = length(distinct([
      for subscription in keys(var.subscription_environment_overrides) : lower(trimspace(subscription))
    ])) == length(var.subscription_environment_overrides)
    error_message = "Override keys must be unique after trimming whitespace and ignoring case."
  }
}
