# Canonical Ownership Maps

Use this reference when the operational model needs a lookup table instead of a narrative boundary explanation.

## Skill Ownership Model

| Skill | Primary owner | When it wins |
| --- | --- | --- |
| `internal-agent-routing-engine` | `internal-router` | Front-door classification, fail-safe selection, and dispatch to one canonical owner |
| `internal-agent-operating-model-engine` | Shared by the four canonical agents | Shared boundary, recommendation, and anti-overlap logic |
| `internal-code-review` | `internal-review-guard` | Tactical review engine for findings and defect-first analysis |
| `internal-agent-development` | `internal-planning-leader` | Non-trivial repository-owned agent authoring |
| `internal-copilot-audit` | `internal-planning-leader` | Catalog audit, drift analysis, and stale-reference review |
| `internal-copilot-docs-research` | `internal-planning-leader` | Contract questions that depend on current GitHub Copilot or MCP behavior |
| `internal-change-impact-analysis` | `internal-planning-leader` | Change-impact and architecture-risk analysis |
| `internal-terraform`, `internal-github-actions`, and runtime-specific internal skills | `internal-fast-executor` for local execution, `internal-planning-leader` when design or rollout dominates | Tactical delivery versus strategy split |
| `obra-*` workflows | Cross-agent support | Mandatory when relevant, absent when irrelevant |

## Retired To Canonical Ownership Mapping

| Retired owner | Canonical owner |
| --- | --- |
| `internal-ai-resource-creator` | `internal-planning-leader` |
| `internal-architect` | `internal-planning-leader` |
| `internal-developer` | `internal-fast-executor` |
| `internal-infrastructure` | `internal-fast-executor` or `internal-planning-leader` when design or rollout dominates |
| `internal-cicd` | `internal-fast-executor` or `internal-planning-leader` when orchestration or tradeoffs dominate |
| `internal-code-review` | `internal-review-guard` |
| `internal-quality-engineering` | `internal-review-guard` for validation and risk, `internal-fast-executor` for a clear fix |
| `internal-aws-*`, `internal-azure-*`, `internal-gcp-*` | `internal-planning-leader` for strategy or design, `internal-fast-executor` for clear local execution |
