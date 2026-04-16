# Kubernetes Routing Matrix

Use this reference when a request touches more than one Kubernetes concern and the winning lane is not obvious from the first prompt.

| Request shape | Primary asset | Why it wins | Adjacent guidance |
| --- | --- | --- | --- |
| Cluster topology, multi-cluster, GitOps operating model, service mesh, platform tenancy | `antigravity-kubernetes-architect` | The pressure is architectural and platform-wide rather than workload-local | Use `internal-kubernetes` only to explain why the strategic lane wins |
| Workload manifests under `k8s/`, `manifests/`, `deploy/`, or Helm templates | `internal-kubernetes-deployment` | The work is about controller choice, rollout behavior, probes, exposure, config, or hardening | Let `awesome-copilot-kubernetes-manifests.instructions.md` auto-apply for YAML hygiene |
| Production rollout safety, readiness, rollback, or observability checks for an existing workload | `internal-kubernetes-deployment` | The platform direction is already chosen and the remaining risk is operational delivery | Pair with repository validation or deployment checks that already exist in the target repo |
| Mixed request that starts broad and then narrows into manifests or rollout settings | `internal-kubernetes` first, then the winning downstream skill | The main value is choosing the lane before doing detailed work | State the split explicitly so only one downstream skill becomes the detailed owner |
| Kubernetes delivery that also changes GitHub Actions workflows | `internal-kubernetes-deployment` plus `internal-github-actions` | One skill owns the workload delivery shape and the other owns CI/CD workflow changes | Keep workflow authoring out of the Kubernetes skill unless the YAML pipeline is the actual target |

## Anti-confusion notes

- A request mentioning GitOps does not automatically make the task strategic; use the strategic lane only when the operating model or platform topology is changing.
- A request mentioning Helm does not automatically make the task architectural; Helm can still be a workload-delivery concern.
- A manifest review is not a platform-design task unless it changes shared cluster policy, tenancy, or traffic architecture.
