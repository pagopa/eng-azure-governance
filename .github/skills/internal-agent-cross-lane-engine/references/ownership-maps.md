# Canonical Ownership Maps

Use this reference when the operational model needs a lookup table instead of a narrative boundary explanation.

The canonical operational model uses direct owner selection. When the winning owner is unclear, fail safe to `internal-planning-leader` instead of a dedicated routing skill.

## Skill Ownership Model

| Skill | Primary owner | When it wins |
| --- | --- | --- |
| `internal-agent-boundary-recommendation-engine` | Shared by the canonical operational agents and repo-only sync command centers | Shared stop-and-recommend protocol when the selected lane no longer fits |
| `internal-agent-cross-lane-engine` | Shared by the four canonical agents | Shared cross-lane boundary, medium-task, and anti-overlap logic |
| `internal-code-review` | `internal-review-guard` | Tactical review engine for findings and defect-first analysis |
| `internal-agent-development` | `internal-planning-leader` | Non-trivial repository-owned agent authoring |
| `internal-copilot-audit` | `internal-planning-leader` | Catalog audit, drift analysis, and stale-reference review |
| `internal-copilot-docs-research` | `internal-planning-leader` | Contract questions that depend on current GitHub Copilot or MCP behavior |
| `internal-change-impact-analysis` | `internal-planning-leader` | Change-impact and architecture-risk analysis |
| `internal-writing-plans` | `internal-planning-leader` | Repository-owned execution-plan authoring under `tmp/superpowers/<clear-action-or-task-name>/` with local structure, path, and language rules |
| `internal-executing-plans` | `internal-planning-leader` | Repository-owned plan application with `done-*` tracking, sequential continuation, and blocker stops |
| `internal-terraform`, `internal-github-actions`, and runtime-specific internal skills | `internal-delivery-operator` for local execution, `internal-planning-leader` when design or rollout dominates | Tactical delivery versus strategy split |
| `obra-*` workflows | Cross-agent support | Mandatory when relevant, absent when irrelevant |

## Retired To Canonical Ownership Mapping

| Retired owner | Canonical owner |
| --- | --- |
| `internal-ai-resource-creator` | `internal-planning-leader` |
| `internal-architect` | `internal-planning-leader` |
| `internal-developer` | `internal-delivery-operator` |
| `internal-infrastructure` | `internal-delivery-operator` or `internal-planning-leader` when design or rollout dominates |
| `internal-cicd` | `internal-delivery-operator` or `internal-planning-leader` when orchestration or tradeoffs dominate |
| `internal-code-review` | `internal-review-guard` |
| `internal-quality-engineering` | `internal-review-guard` for validation and risk, `internal-delivery-operator` for a clear fix |
| `internal-aws-*`, `internal-azure-*`, `internal-gcp-*` | `internal-planning-leader` for strategy or design, `internal-delivery-operator` for clear local execution |
