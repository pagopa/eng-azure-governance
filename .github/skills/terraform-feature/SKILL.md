---
name: terraform-feature
description: Add or modify Terraform resources, variables, outputs, and data sources.
---

# Terraform Feature Skill

## When to use
- Add or modify resources.
- Add/update variables and outputs.
- Add data sources.

## Mandatory rules
- Preserve naming and folder conventions.
- Use `snake_case` for Terraform identifiers.
- Add `description` and `type` to variables.
- Add `description` to outputs.
- Avoid hardcoded values.
- Apply tags where supported.

## Minimal example
```hcl
variable "project_id" {
  description = "Project identifier"
  type        = string
}

resource "aws_s3_bucket" "logs" {
  bucket = "${var.project_id}-logs"
}

output "logs_bucket_id" {
  description = "Logs bucket id"
  value       = aws_s3_bucket.logs.id
}
```

## Validation
- `terraform fmt`
- `terraform validate`
- Review `terraform plan`
