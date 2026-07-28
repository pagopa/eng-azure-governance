---
description: Helm chart and values review checks for secure, deterministic Kubernetes delivery.
applyTo: "**/Chart.yaml,**/values.yaml,**/values*.yaml"
excludeAgent: "cloud-agent"
---

# Helm Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Flag chart and dependency versions that are missing, floating, or not reproducible.
- Flag image tags that are mutable or not pinned to deterministic versions.
- Flag values that enable privileged pods, broad capabilities, or missing security context hardening.
- Flag missing or unsafe defaults for resource requests and limits.
- Flag service or ingress exposure that is broader than the stated workload intent.
- Flag plaintext secrets or sensitive values committed in chart values files.
- Flag missing readiness, liveness, or startup probe defaults where workloads require health gating.
