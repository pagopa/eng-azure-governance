---
name: terraform-module
description: Create or modify reusable Terraform modules with standard file layout and validation.
---

# Terraform Module Skill

## When to use
- Building a new reusable Terraform module.
- Refactoring resources into a module.
- Standardizing existing modules.

## Standard layout
- `main.tf`
- `variables.tf`
- `outputs.tf`
- `versions.tf`
- `README.md`

## Mandatory rules
- Use typed variables with `description`.
- Use outputs with `description`.
- Avoid hardcoded IDs and secrets.
- Preserve stable module input/output contracts.

## Minimal example
```hcl
# variables.tf
variable "name" {
  description = "Resource base name"
  type        = string
}

# outputs.tf
output "id" {
  description = "Created resource id"
  value       = aws_s3_bucket.this.id
}
```

## Validation
- `terraform fmt`
- `terraform validate`
- Module example/consumer plan review
