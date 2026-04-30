# AGENTS.md - Instruction Architecture Bridge

This file is the stable entrypoint for the repository instruction architecture.

## Role

- `AGENTS.md` is the main orientation document, the cross-surface bridge, and the precedence anchor.
- Keep this file stable, strategic, and free of volatile inventory.
- Treat rules as canonical here unless a narrower scoped instruction explicitly owns an exception.

## Cross-Surface Contract

1. Use `.github/copilot-instructions.md` as the repo-wide Copilot projection.
2. Use `.github/INVENTORY.md` for the exact live catalog of instructions, skills, and agents.
3. Use `.github/instructions/` for path-specific or domain-specific projections.
4. Use `.github/skills/` and `.github/agents/` only when they are relevant to the current task.
5. Keep policy, projections, and inventory separate instead of mixing them into one file.
6. If `docs/architecture.md` exists in the current repository, treat it as the per-repo architecture contract: read it before reasoning about repository purpose, components, system boundaries, or runtime fit, and update it in the same change when behavior, components, or boundaries move. This file is intentionally not part of the synced baseline; each repository owns its own `docs/architecture.md`. If the file is absent, fall back to inspecting the repository structure on disk and do not invent architecture facts.

## Precedence Model

- `AGENTS.md` owns repository-wide defaults, rule placement, and bridge behavior.
- `.github/copilot-instructions.md` projects the repo-wide behavior that must remain visible in native Copilot flows and must stay aligned with this file.
- Narrower scoped instructions may override defaults only inside their declared scope.
- Before adding a new policy, decide whether it truly belongs at repository scope; prefer the smallest specific instruction, skill, agent, or configuration that fully owns the behavior, and promote it to `AGENTS.md` only when it changes cross-surface governance or applies across the AI configuration baseline.
- When rules conflict, prefer the smallest valid scope; if scope is equal, follow the canonical rule stated here and remove the conflicting duplicate.

## Language Default

- The default authoring language for repository artifacts is English unless a scoped instruction explicitly overrides it.
- User chat may be Italian.
- Keep language exceptions explicit and local instead of restating broader prohibitions across the catalog.
- Repository-owned execution-plan artifacts under `tmp/superpowers/<clear-action-or-task-name>/` may default to Italian when the local planning policy applies; this exception stays local to those plan files and does not change the repository-wide English default.

## Naming Contract

- Repository-owned resources created in `cloud-strategy.github` use the `internal-*` prefix by default.
- Repository-owned resources created in other repositories use the `local-*` prefix.
- The `local-*` prefix is also reserved, inside this standards repository, for repo-owned tooling that must remain source-of-truth here and must NOT propagate to consumer repositories during sync (for example, the sync command-center agents and their paired engine skills). These assets stay excluded from the synced baseline by design.
- Imported upstream resources keep the `<short-repo>-<original-resource-name>` form.

## Resource Model

- Treat prefixes as origin and ownership markers first. Do not use them as a rigid proxy for strategic, tactical, or operational level.
- Evaluate resources on two axes: origin/ownership and dominant role.
- `obra-*` resources are cross-cutting workflow assets. They often help with strategic framing, but may govern tactical or operational work when relevant.
- `internal-*` resources are the canonical repository-owned layer. They are tactical by default, but may also be strategic or operational when their contract says so.
- Imported upstream resources remain support depth by default. Overlap alone is not enough to fork or wrap them; prefer a repository-owned wrapper or replacement only when routing, governance, terminology, output shape, or safety expectations require repo-local ownership.
- During catalog review or rationalization, imported assets in domains already covered by a credible internal owner must be evaluated as `keep as depth`, `wrap under the internal owner`, or `retire`; do not collapse that decision to a binary keep/delete choice.
- Keep imported upstream assets verbatim by default. Allow a direct in-place override only for a strong repo-specific need that the user explicitly counter-validates, and register that override in the `local-agent-sync-external-resources` skill bundle so future refreshes can replay it safely.
- `local-*` resources remain consumer-local extensions in target repositories. In this standards repository, the `local-*` prefix is also used for repo-owned tooling that intentionally must not be synced to consumers (for example, sync command centers and their paired engine skills); these assets remain source-of-truth here and are excluded from the synced baseline.
- When overlap exists, prefer the repository-owned internal owner as canonical and use imported depth as support unless no credible internal owner exists.

## Operational Owner Model

- `internal-delivery-operator`, `internal-planning-leader`, `internal-review-guard`, and `internal-critical-master` remain the canonical repository-owned operational agents.
- The canonical operational model uses direct entry instead of a repository-owned front-door router.
- When the right lane is unclear, prefer `internal-planning-leader` as the safe fallback.
- Canonical owners remain recommendation-only when their boundary breaks and are not subagent-invoked by default.
- Any future automation between canonical owners must be explicit, narrow, one-directional, and must not create all-to-all dispatch or nested ping-pong.

## Projection Rules

- Keep repo-wide Copilot behavior in `.github/copilot-instructions.md`.
- Keep local self-containment in scoped instruction files only when it improves the consumer experience and does not create drift.
- Keep volatile inventory in `.github/INVENTORY.md`, never here.
- When introducing a new source-managed catalog family or a new human-readable catalog summary surface, update inventory generation, sync discovery, and validator coverage in the same change so `.github/INVENTORY.md` is not the only surface aware of it.
- Do not add hand-maintained catalog matrices or counts beside `.github/INVENTORY.md` unless they are generated from the filesystem or covered by validation.
- Keep `internal-sync-*` assets sync-specific. They may reference root governance, but they do not replace canonical ownership in this file or `.github/copilot-instructions.md`.
- When a sync or catalog workflow changes a repository-wide default, update the canonical owner first and then realign downstream projections or sync surfaces in the same pass.
- Do not treat removed validators, sync scripts, contract tests, or historical aliases as active policy unless they exist on disk and are reintroduced deliberately.

## Consumer Override Layer

- This standards repository owns the sync seed template at `.github/copilot-instructions.override.md.template`.
- Consumer repositories may keep `.github/copilot-instructions.override.md` as the consumer-local exception layer materialized from that template by sync.
- That file may override synced defaults from `AGENTS.md` or `.github/copilot-instructions.md` only inside the consumer repository and only when each exception states the overridden baseline rule, local scope, reason, and required disclosure.
- If the target file exists but declares no active overrides, keep the synced baseline authoritative.
- When a response follows a local override, it must say that a consumer-local exception is in effect and cite `.github/copilot-instructions.override.md`.
- Keep the target override file local in effect even when seeded by sync. Do not treat it as inventory, and do not use it to collapse the separate roles of `AGENTS.md`, `.github/copilot-instructions.md`, and `.github/INVENTORY.md`.
- The local override layer must not redefine the ownership meaning of `internal-*`, `local-*`, or `internal-sync-*`; use it for repo-local exceptions, not for replacing the bridge model.

## Retained Learning

- Root `LESSONS_LEARNED.md` is the repository learning ledger for durable lessons discovered during repository work, regardless of phase.
- Record or codify a durable lesson as soon as it becomes clear enough to be reusable; do not wait for task completion only because the work is still in planning, review, debugging, or implementation.
- When a validator, IDE, schema check, or runtime error overturns an earlier implementation assumption, re-evaluate retained learning immediately instead of treating the correction as task-local by default.
- When correctness depends on vendor-owned workflow semantics, schema constraints, or context availability, read the primary documentation before editing or asserting that a change is valid.
- Keep `LESSONS_LEARNED.md` non-canonical. It must not replace `AGENTS.md`, `.github/copilot-instructions.md`, scoped instructions, skills, or agents.
- Keep `LESSONS_LEARNED.md` append-preserving by default: preserve unrelated rows already on disk, including local uncommitted lessons, and change a specific row only when that same lesson is being codified, disproven, narrowed, or deduplicated.
- Durable corrections to repeated or consequential misapplication of existing repository rules may also be retained as lessons.
- Keep detailed retained-learning behavior in `.github/copilot-instructions.md`; keep only the strategic boundary here.

## Volatile Artifacts

- Transient planning, brainstorming, and other Superpowers-generated working files must not be written under `docs/`.
- When such artifacts are needed inside this repository, write them under `tmp/superpowers/`.
- Create or reuse `tmp/superpowers/<clear-action-or-task-name>/` only for retained repository-owned planning that must survive the current turn because the work is non-banal, crosses turns, spans macro-categories, needs handoff, tracking, or provenance, or preserves tradeoffs worth review.
- Keep retained execution plans as numbered Markdown files: a single `01-...md` file when one macro-category is enough, or multiple numbered files such as `01-contesto-e-vincoli.md`, `02-implementazione.md`, and `03-validazione.md` when the work spans multiple macro-categories.
- Keep unresolved questions, doubts, or user decisions in `dubbi-e-domande.md`; this file stays separate from executable plan files and remains outside the plan-and-apply loop.
- During execution, create matching `done-*` files, move completed items into them, remove them from the active numbered source file, and continue through the remaining numbered plan files until the work is finished or a real blocker requires user input.
