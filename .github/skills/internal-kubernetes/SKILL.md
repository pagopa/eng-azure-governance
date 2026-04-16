---
name: internal-kubernetes
description: Use when the task involves Kubernetes but the winning lane is not obvious yet, or when the work spans platform architecture, manifest authoring, rollout safety, and production readiness across the repository-owned and imported Kubernetes skills.
---

# Internal Kubernetes

Use this skill to choose the right Kubernetes lane before drafting guidance or editing delivery assets.

## Workflow

1. Classify the pressure.
   Decide whether the request is mainly about platform strategy, workload delivery authoring, or rollout and recovery.
2. Pick the winning Kubernetes asset.
   Use `antigravity-kubernetes-architect` for platform architecture and `internal-kubernetes-deployment` for workload manifests, rollout safety, and production hardening.
3. Keep adjacent guidance scoped.
   Let `awesome-copilot-kubernetes-manifests.instructions.md` auto-apply on manifest files instead of restating YAML rules here.
4. Return one clear next lane.
   State which skill wins, why it wins, and what validation or artifact should follow.

## Winning lanes

- Strategic platform architecture: cluster topology, GitOps operating model, service mesh, multi-cluster shape, and platform security boundaries.
- Tactical workload authoring: workload shape, controller choice, service exposure, ingress, probes, autoscaling, config, and secret handling.
- Operational rollout and recovery: rollout strategy, rollback, observability hooks, network-policy verification, and production-readiness checks.

Load `references/routing-matrix.md` when the request mixes platform, manifest, and rollout concerns or when the boundary between strategy and delivery is unclear.

## Guardrails

- Do not use this skill to replace the imported strategist or the repository-owned deployment skill; it exists to orchestrate them.
- Do not describe this skill as a router for the whole catalog; it only chooses the right Kubernetes lane.
- Do not escalate to GitOps, service mesh, or multi-cluster design unless the user is actually changing platform behavior.
- Do not treat a manifest edit as platform architecture work just because the workload runs on Kubernetes.

## Output requirements

- selected Kubernetes lane
- winning skill or instruction and why
- key assumptions or missing inputs
- next artifact or validation step
