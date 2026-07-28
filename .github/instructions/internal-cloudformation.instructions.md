---
description: CloudFormation and SAM review checks for secure, drift-aware, production-safe templates.
applyTo: "**/*.template.yaml,**/*.template.yml,**/template.yaml,**/template.yml,**/*.cfn.yaml,**/*.cfn.yml,**/*.cfn.json"
excludeAgent: "cloud-agent"
---

# CloudFormation Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Flag IAM policies and roles that exceed least-privilege intent.
- Flag hardcoded secrets, account IDs, or static ARNs that should be parameterized.
- Flag stateful resources missing `DeletionPolicy` or `UpdateReplacePolicy` safeguards.
- Flag parameter definitions missing allowed values, constraints, or safe defaults where required.
- Flag changes that can trigger replacement or export/import breakage without an explicit migration signal.
- Flag unpinned or mutable transform and nested-stack references.
- Flag unsafe cross-stack exports or implicit coupling that increases rollback risk.
