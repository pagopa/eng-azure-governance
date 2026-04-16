# Terraform Template Examples

## Minimal Feature Example

```hcl
variable "project_id" {
  description = "Project identifier"
  type        = string
}

resource "aws_s3_bucket" "logs" {
  bucket = "${var.project_id}-logs"

  tags = {
    Project = var.project_id
  }
}

output "logs_bucket_id" {
  description = "Logs bucket id"
  value       = aws_s3_bucket.logs.id
}
```

## Minimal Module Example

```hcl
# variables.tf
variable "name" {
  description = "Resource base name"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string

  validation {
    condition     = contains(["dev", "uat", "prod"], var.environment)
    error_message = "Must be one of: dev, uat, prod."
  }
}

# main.tf
resource "aws_s3_bucket" "this" {
  bucket = "${var.name}-${var.environment}"

  tags = {
    Name        = var.name
    Environment = var.environment
  }
}

# outputs.tf
output "bucket_id" {
  description = "Created bucket id"
  value       = aws_s3_bucket.this.id
}
```
