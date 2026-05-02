---
name: internal-agent-boundary-recommendation-engine
description: Use when a repository-owned internal agent needs a consistent stop-and-recommend response after the user selected the wrong lane or the current lane stops being the best fit.
---

# Internal Agent Boundary Recommendation Engine

Use this skill as the shared lane-mismatch engine for repository-owned internal agents that must stop, explain the mismatch, and recommend the better next option without hidden delegation.

## When to use

- A repository-owned internal agent was selected for a request it is not optimized to own.
- New information changes the winning lane after the current agent already started.
- Several related agents need the same stop-and-recommend behavior and that logic should not be duplicated in every agent body.

## Goals

- Stop before doing off-lane work.
- Explain the concrete mismatch in plain language.
- Recommend exactly one better owner when the next lane is clear.
- Fail safe to `internal-planning-leader` when more than one plausible owner remains.
- Keep the recommendation user-visible and recommendation-only.

## Shared Stop Protocol

1. State that the current lane is not the best fit.
2. Name the concrete reason the boundary broke.
3. Recommend one better owner and give one reason.
4. If the next owner is still ambiguous, recommend `internal-planning-leader` instead of offering multiple half-confident options.
5. Do not open a hidden second lane and do not continue with off-lane work.

## Recommendation Matrix

| Current agent | When the boundary breaks | Recommend |
| --- | --- | --- |
| `internal-delivery-operator` | Ambiguity, governance, or non-trivial authoring dominates | `internal-planning-leader` |
| `internal-delivery-operator` | Review, regression, or validation becomes the main need | `internal-review-guard` |
| `internal-delivery-operator` | Assumption stress-testing becomes the main need | `internal-critical-master` |
| `internal-planning-leader` | The next step is clear local execution with concrete verification | `internal-delivery-operator` |
| `internal-planning-leader` | Defect-first validation or merge readiness is now the main need | `internal-review-guard` |
| `internal-planning-leader` | The plan must be pressure-tested before action | `internal-critical-master` |
| `internal-review-guard` | Findings show missing design, routing, or plan ownership | `internal-planning-leader` |
| `internal-review-guard` | Weak reasoning needs a pressure test more than a technical review | `internal-critical-master` |
| `internal-review-guard` | The review lane is done and the next step is a clear local fix | `internal-delivery-operator` |
| `internal-critical-master` | The next step is a clear implementation or apply action | `internal-delivery-operator` |
| `internal-critical-master` | The framing or plan must be reformulated first | `internal-planning-leader` |
| `internal-critical-master` | The next step is evidence-based validation of a concrete change | `internal-review-guard` |
| `local-sync-external-resources` | The source-side catalog direction is still ambiguous or needs repo-owned authoring decisions first | `internal-planning-leader` |
| `local-sync-external-resources` | The real job is consumer-repository baseline propagation | `local-sync-global-copilot-configs-into-repo` |
| `local-sync-external-resources` | The work reduced to a clear local edit outside catalog-governance scope | `internal-delivery-operator` |
| `local-sync-global-copilot-configs-into-repo` | The real job is source-side catalog governance in this repository | `local-sync-external-resources` |
| `local-sync-global-copilot-configs-into-repo` | The request is source-side redesign, agent authoring, or governance restructuring | `internal-planning-leader` |
| `local-sync-global-copilot-configs-into-repo` | Only a clear target-local execution step remains after the sync contract is settled | `internal-delivery-operator` |

## Agent-Specific Notes

- `internal-critical-master` may need to ask whether the current analysis should be saved before recommending another owner.
- Repo-only sync agents may name the mode or scope mismatch before giving the shared recommendation.
- Do not recommend returning to the same agent.
- Do not recommend multiple alternatives unless the user explicitly asks for options.

## Validation

- The recommendation names an exact next owner unless ambiguity still remains.
- The response stops before off-lane execution starts.
- The mismatch reason is concrete, not prestige-based.
- The recommendation stays user-visible and does not rely on hidden agent dispatch.
