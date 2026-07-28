---
description: Terraform authoring standards for readability, typed interfaces, and validation-first delivery.
applyTo: "**/*.tf"
excludeAgent: "cloud-agent"
---

# Terraform Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Flag variables or outputs missing a `description`.
- Flag variables missing an explicit `type`.
- Verify variable and output types are explicit and match actual usage.
- Flag provider, module, or version constraints that are missing or too loose.
- Check resource changes for destructive replacement or drift-risk behavior.
- Verify IAM and network changes follow least-privilege intent.
- Report hidden dependencies that rely on implicit ordering.
- Check naming, tagging, and state-sensitive references for consistency.
- Flag hardcoded IDs, ARNs, subscription IDs, or secrets.
- Flag taggable resources without tags.
- Flag non-`snake_case` Terraform identifiers.
- Flag `terraform state mv`, `terraform state rm`, or `terraform import` changes without a documented migration note.
- Flag missing validation or precondition logic on critical inputs.
