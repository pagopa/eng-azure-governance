output "subscriptions_by_environment" {
  description = "Display names of the active subscriptions assigned to each environment"
  value       = { for environment, subscriptions in local.subscriptions_by_environment : environment => sort(keys(subscriptions)) }

  precondition {
    condition = alltrue([for subscriptions in values(local.active_subscriptions_by_name) : length(subscriptions) == 1])
    error_message = format("Enabled subscriptions outside subscription_blacklist must have unique display names to preserve Terraform module identities: %s.", join(", ", [
      for name, subscriptions in local.active_subscriptions_by_name : name if length(subscriptions) > 1
    ]))
  }

  precondition {
    condition = alltrue([for environment in values(local.subscription_environments) : environment != null])
    error_message = format("Set subscription_environment_overrides or subscription_blacklist for subscriptions without an environment prefix: %s.", join(", ", [
      for name, environment in local.subscription_environments : name if environment == null
    ]))
  }
}
