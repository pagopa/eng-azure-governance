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

## Naming Contract

- Repository-owned resources created in `cloud-strategy.github` use the `internal-*` prefix.
- Repository-owned resources created in other repositories use the `local-*` prefix.
- Imported upstream resources keep the `<short-repo>-<original-resource-name>` form.

## Resource Model

- Treat prefixes as origin and ownership markers first. Do not use them as a rigid proxy for strategic, tactical, or operational level.
- Evaluate resources on two axes: origin/ownership and dominant role.
- `obra-*` resources are cross-cutting workflow assets. They often help with strategic framing, but may govern tactical or operational work when relevant.
- `internal-*` resources are the canonical repository-owned layer. They are tactical by default, but may also be strategic or operational when their contract says so.
- Imported upstream resources remain support depth by default. Overlap alone is not enough to fork or wrap them; prefer a repository-owned wrapper or replacement only when routing, governance, terminology, output shape, or safety expectations require repo-local ownership.
- `local-*` resources remain consumer-local extensions. They are usually tactical or operational, but may be strategic when a consumer repository needs explicit local governance.
- When overlap exists, prefer the repository-owned internal owner as canonical and use imported depth as support unless no credible internal owner exists.

## Operational Owner Model

- `internal-router` remains the only active front-door router for the canonical operational catalog.
- `internal-router` may hand work to one selected canonical owner without becoming the domain owner itself; non-router canonical agents may be entered directly or by router handoff, but remain recommendation-only when their boundary breaks unless a narrower scoped contract explicitly allows invoking `internal-router` as a second parallel lane while keeping `internal-router` as the only router.

## Projection Rules

- Keep repo-wide Copilot behavior in `.github/copilot-instructions.md`.
- Keep local self-containment in scoped instruction files only when it improves the consumer experience and does not create drift.
- Keep volatile inventory in `.github/INVENTORY.md`, never here.
- Keep `internal-sync-*` assets sync-specific. They may reference root governance, but they do not replace canonical ownership in this file or `.github/copilot-instructions.md`.
- When a sync or catalog workflow changes a repository-wide default, update the canonical owner first and then realign downstream projections or sync surfaces in the same pass.
- Do not treat removed validators, sync scripts, contract tests, or historical aliases as active policy unless they exist on disk and are reintroduced deliberately.

## Consumer Override Layer

- Consumer repositories may keep a non-mirrored `.github/local-copilot-overrides.md` file as a consumer-owned local exception layer.
- That file may override synced defaults from `AGENTS.md` or `.github/copilot-instructions.md` only inside the consumer repository and only when each exception states the overridden baseline rule, local scope, reason, and required disclosure.
- If the file exists but declares no active overrides, keep the synced baseline authoritative.
- When a response follows a local override, it must say that a consumer-local exception is in effect and cite `.github/local-copilot-overrides.md`.
- Keep the local override file local. Do not mirror it from this standards repository, do not treat it as inventory, and do not use it to collapse the separate roles of `AGENTS.md`, `.github/copilot-instructions.md`, and `.github/INVENTORY.md`.
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
