---
description: Best practices for Azure DevOps Pipeline YAML files
applyTo: "**/azure-pipelines.yml,**/azure-pipelines*.yml,**/*.pipeline.yml"
excludeAgent: "cloud-agent"
---

# Azure Pipelines Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify trigger, path, and branch filters match intended CI and deployment scope.
- Flag unpinned tasks, mutable image references, or agent pools that reduce determinism.
- Check secret handling: no hardcoded credentials and least-privilege service connections.
- Validate stage and job dependencies so promotion order and gating are explicit.
- Confirm test and quality gates are present where builds produce deployable artifacts.
- Flag missing timeout, retry, or fail-fast safeguards on long or risky steps.
- Verify artifact naming and retention are explicit when downstream jobs consume outputs.
- Report approval and environment gate gaps for production-impacting deployment stages.
