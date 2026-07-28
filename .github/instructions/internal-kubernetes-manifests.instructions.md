---
description: Best practices for Kubernetes YAML manifests including labeling conventions, security contexts, pod security, resource management, probes, and validation commands
applyTo: "k8s/**/*.yaml,k8s/**/*.yml,manifests/**/*.yaml,manifests/**/*.yml,deploy/**/*.yaml,deploy/**/*.yml,charts/**/templates/**/*.yaml,charts/**/templates/**/*.yml"
excludeAgent: "cloud-agent"
---

# Kubernetes Manifest Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify labels and selectors are consistent to prevent broken workload routing.
- Flag missing or unsafe `securityContext` settings on pods and containers.
- Check CPU and memory requests/limits for scheduler and stability safety.
- Verify probes are defined and aligned with actual container startup behavior.
- Report privilege escalation, host namespace, or broad volume-mount risks.
- Check service exposure and ingress changes for unintended public access.
- Flag rollout settings that increase outage risk during updates.
- Verify API versions and kinds are supported and not deprecated.
