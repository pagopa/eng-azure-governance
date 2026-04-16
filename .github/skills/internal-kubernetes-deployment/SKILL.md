---
name: internal-kubernetes-deployment
description: Use when authoring or reviewing Kubernetes workload manifests, service exposure, probes, autoscaling, rollout strategy, or production-readiness settings for an already-chosen platform or cluster model.
---

# Internal Kubernetes Deployment

Use this skill for operational Kubernetes delivery work after the platform direction is already known.

## Boundary

- Use this skill only after the platform or cluster direction is already chosen.
- If the real question is cluster architecture, GitOps operating model, service mesh, or multi-cluster strategy, treat it as a platform-design problem rather than a manifest-delivery task.
- Keep this skill focused on workload manifests, rollout safety, and production hardening.

## Operational Workflow

1. Identify workload type: stateless, stateful, batch, or platform component.
2. Choose the right controller: Deployment, StatefulSet, Job, or CronJob.
3. Define service exposure and traffic flow.
4. Choose the packaging and delivery mode.
5. Add health, scaling, security, and policy settings.
6. Validate rollout and rollback behavior.

## Manifest Priorities

- Explicit resource requests and limits
- Readiness and liveness probes
- ConfigMaps for non-secret config
- Secrets for sensitive values
- Service and Ingress only when the traffic model needs them
- NetworkPolicy when east-west or egress boundaries matter
- Pod disruption and rollout settings for availability

## Delivery Extensions

- Prefer raw manifests by default; add Helm only when repeated installs, versioned packaging, or environment overlays justify chart maintenance.
- Treat service mesh integration as conditional: configure traffic policy, mTLS, and mesh telemetry only when the cluster already runs a mesh or the platform standard requires it.
- Prefer controller-driven delivery such as GitOps only when the team already operates that model and the rollout ownership is explicit.
- Let `awesome-copilot-kubernetes-manifests.instructions.md` own YAML-level manifest conventions when the target files are manifests.

## Operational Rules

- Do not deploy bare Pods for managed workloads.
- Keep images versioned and reproducible.
- Prefer rolling updates with bounded surge and unavailability.
- Use HPA only when the workload exposes a sensible scaling signal.
- Make failure modes visible through probes and events.
- Verify workload, Service, Ingress, and policy state together; a healthy Pod alone does not prove a complete deployment.
- Add dashboards, alerts, and scrape annotations only when they match the platform's observability standard.

## Security Rules

- Run as non-root when possible.
- Minimize capabilities.
- Use read-only filesystems when feasible.
- Keep secret usage narrow and explicit.
- Avoid over-broad service account permissions.
- Use NetworkPolicy and namespace boundaries to narrow runtime traffic.

## Anti-Patterns

- Missing resource limits in shared clusters
- Using probes that only prove the process exists
- Introducing Helm, GitOps, or service mesh just to look "enterprise"
- Stuffing secrets into ConfigMaps
- Exposing workloads publicly without clear ingress intent
- Treating a successful `kubectl apply` as proof of production readiness

## Output Expectations

When producing guidance, include:

- Recommended workload shape
- Required manifest primitives
- Packaging and delivery choice
- Rollout and recovery considerations
- Security, policy, and observability gaps
