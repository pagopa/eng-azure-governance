# Agents Catalog

This folder contains optional custom agents for focused tasks.

## Resolution order
1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply explicit user request and selected agent behavior (agent-first).
3. Apply matching `instructions/*.instructions.md` (`applyTo` by path).
4. Apply prompt and referenced skill details.

## Recommended routing
- Read-only: `Planner`, `Reviewer`, `SecurityReviewer`, `WorkflowSupplyChain`, `TerraformGuardrails`, `IAMLeastPrivilege`.
- PR-focused: `PRWriter`.
- Write-capable: `Implementer`.

## Why generic core agents
- `Planner`, `Implementer`, and `Reviewer` are workflow roles, not language roles.
- Technology is resolved from file paths and prompt inputs (for example, `**/*.py` -> Python instructions).
- Avoid creating per-language triplets unless repeated failures justify a dedicated specialist.

## Selection guide
1. Use `Planner` at design stage.
2. Use `Implementer` for execution after requirements are stable.
3. Use `Reviewer` for non-security quality gates.
4. Use `TerraformGuardrails` and `IAMLeastPrivilege` on policy/infrastructure changes.
5. Use `WorkflowSupplyChain` on workflow changes.
6. Use `PRWriter` to create or update PR title/body from template and diff.
7. Use `SecurityReviewer` as final security gate.
