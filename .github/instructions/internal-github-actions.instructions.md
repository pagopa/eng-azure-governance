---
description: Baseline standards for GitHub Actions workflows and composite actions with SHA pinning, least privilege, and deterministic execution.
applyTo: "**/workflows/**,**/actions/**/action.y*ml"
excludeAgent: "cloud-agent"
---

# GitHub Actions Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Flag action and container references that are not pinned to immutable SHAs or digests.
- Verify `permissions` are least privilege at workflow and job scope.
- Check secret usage to ensure no hardcoded sensitive values in workflows.
- Flag long-lived cloud credentials in secrets where OIDC should be used.
- Flag production deploy jobs without protected `environment` reviewers.
- Flag `workflow_dispatch` inputs consumed by shell or deploy steps without validation.
- Report unsafe event triggers or trust-boundary violations for untrusted code.
- Verify concurrency, timeout, and cancellation controls for long-running jobs.
- Check cache and artifact keys for deterministic behavior and retention clarity.
- Flag required-check naming drift that can break branch protection enforcement.
- Report context misuse that fails at parse time or queue time.
