# Global Copilot Instructions

You are an expert software and platform engineer. Protect correctness, security, simplicity, and maintainability in every change.

## Repository Role

- Treat this repository as a Copilot customization and governance repository unless the target files prove otherwise.
- Inspect nearby files before editing and follow the existing naming, frontmatter, and directory patterns.
- Use only repository evidence that exists on disk. Do not invent runtimes, validators, sync flows, or test suites.
- Treat imported non-`internal-*` assets as upstream resources; keep them verbatim unless the user explicitly asks for a refresh, replacement, or local fork.

## Precedence And Projections

1. `AGENTS.md` is the strategic entrypoint, the precedence anchor, and the cross-surface bridge.
2. This file is the repo-wide Copilot projection and should keep only the behavior that must remain visible in native Copilot flows.
3. `.github/copilot-code-review-instructions.md` and `.github/copilot-commit-message-instructions.md` apply when the task is review or commit authoring.
4. Matching `.github/instructions/*.instructions.md` files provide scoped or domain-specific guidance and may override defaults inside their declared scope.
5. Skills and agents are on-demand operational assets; use them only when relevant.
6. `.github/INVENTORY.md` is the live catalog of managed assets and is never replaced by `AGENTS.md`.
7. If `.github/local-copilot-overrides.md` exists, read it before relying on synced repo-wide defaults; it is the consumer-local exception layer authorized by `AGENTS.md`.

- `internal-sync-*` assets stay sync-specific and must not become second canonical homes for repository-wide policy.
- When repository-wide defaults change, update `AGENTS.md` first, then refresh this file, then realign narrower governance assets that reference the change.
- When source-managed guidance from this repository is mirrored into consumer repositories, phrase source-side rules conditionally so they remain true in targets and do not imply that the target repository is the source of truth.
- `.github/local-copilot-overrides.md` may override synced defaults from `AGENTS.md` or this file only when the exception makes the conflict, scope, reason, and required disclosure explicit.
- If `.github/local-copilot-overrides.md` exists but declares no active overrides, keep following the synced baseline.
- When following a local override instead of the synced baseline, say that a consumer-local exception is in effect and cite `.github/local-copilot-overrides.md`.
- Do not treat the local override file as inventory or as a replacement for the bridge, projection, and catalog split.

## Language Projection

- User chat may be Italian.
- The default authoring language for repository artifacts is English unless a scoped instruction explicitly overrides it.
- Keep any exception local and explicit instead of restating stricter global variants across the catalog.

## Catalog Model

- Prefixes encode origin and ownership first, not a rigid abstraction level.
- Evaluate resources on two axes: origin/ownership and dominant role.
- `obra-*` skills are the cross-cutting workflow lane. They often improve strategic framing, but may also govern tactical or operational work when relevant.
- `internal-*` skills are the canonical repository-owned layer. They are tactical by default, but may also own strategic or operational work when their contract says so.
- Imported non-`internal-*` assets are support-only depth by default. Prefer a repository-owned internal owner when one exists, and add wrappers or replacements only when repo-specific governance, routing, terminology, output shape, or safety expectations require it.
- `local-*` assets are consumer-local extensions. They are usually tactical or operational and become strategic only when local governance explicitly needs it.
- `internal-router`, `internal-fast-executor`, `internal-planning-leader`, `internal-review-guard`, and `internal-critical-challenger` are the canonical repository-owned operational agents.
- Only `internal-router` actively routes. It may hand work to one selected canonical owner without doing that owner's domain work itself, while non-router canonical agents stay boundary-driven and recommendation-only when a better owner is needed unless a scoped contract explicitly allows them to invoke `internal-router` as a second parallel lane without selecting the downstream owner themselves.
- `internal-sync-*` agents are specialized sync command centers and stay outside the canonical operational-owner model.

## Non-Negotiables

- Least privilege.
- No hardcoded secrets.
- Preserve existing conventions unless the task explicitly changes them.
- Do not modify `README.md` files unless explicitly requested.
- Update non-README technical docs when behavior or governance changes.
- Keep policy separate from inventory.

## Implementation Discipline

- Prefer the simplest correct change.
- Keep business logic separated from I/O and infrastructure concerns.
- Apply only the instruction files relevant to the files being changed.
- For vendor-owned or schema-driven configuration surfaces, read the primary documentation before editing whenever correctness depends on platform-specific semantics such as context availability, expression scope, or validation rules; do not rely on memory alone.
- For repository-owned skill work, validate frontmatter before refining body wording or token shape.
- For source-side repository-owned standards work that deepens parallel skill families, stage planning in `tmp/superpowers/`, make anti-scope explicit, and close parity gaps in existing `Common mistakes`, `Validation`, and current reference depth before adding optional new skills, validators, or shared assets.
- Keep repository-owned skill `description:` lines trigger-first, and do not rewrite a working route during token optimization unless improving retrieval is the explicit goal.
- For provider-specific cloud skills, keep guidance provider-native and omit cross-cloud comparison or provider-selection content when provider choice is already upstream of skill activation.
- Prefer `references/` over new `scripts/` for static checklists, lookup tables, and starter templates; add scripts only when the workflow is deterministic, repeated, and execution-heavy.
- Keep Python tests under the repository-root `tests/` tree with mirrored source paths, and make Bash wrappers runnable with internal defaults plus optional overrides.
- Run the applicable validation that actually exists for the files you changed.
- If a dedicated validator, sync script, or contract test suite does not exist, report the gap and use the closest existing verification instead.
- Do not add unrequested abstractions, logging, or refactors.

## Repository Workflow Reminders

- PR content must follow `.github/PULL_REQUEST_TEMPLATE.md` in exact section order.
- For GitHub Actions pinning, each full SHA must include an adjacent comment with a release or tag reference.
- `CODEOWNERS` may keep `@your-org/platform-governance-team` only in template repositories; consumer repositories must replace that placeholder before review enforcement.

## Retained Learning

- Whenever work reveals a new durable lesson, regardless of whether the task is in planning, review, debugging, or implementation, check whether it was already codified in repository resources when discovered.
- Also treat a repeated or consequential misapplication of an already-codified repository rule as a lesson when the correction is likely to prevent the same mistake in future work.
- When a validator, IDE, schema check, or runtime error overturns an earlier assumption, immediately re-check whether that correction is durable enough to retain or codify.
- Before finalizing such a correction, read the primary documentation for the relevant platform or schema instead of relying on memory or partial recall.
- Before editing repository-root `LESSONS_LEARNED.md`, read its current on-disk contents and treat them as the source of truth for in-progress local lessons, including uncommitted rows already present on disk.
- When a durable lesson is clear and still uncodified, append one concise, reusable row to the pending table in `LESSONS_LEARNED.md` instead of waiting for task completion; do not regenerate, reorder, or rewrite unrelated rows.
- If you decide not to record a lesson after such a correction, make that decision explicit in the completion report with a short reason.
- Treat `LESSONS_LEARNED.md` as a learning ledger, not as canonical policy. Do not dump transient notes, full debugging timelines, sensitive content, or conversational noise into it.
- Preserve unrelated existing lessons in `LESSONS_LEARNED.md`, including local uncommitted ones already on disk.
- If a lesson is later disproven, narrowed, deduplicated, or codified elsewhere in the same task, update or remove only that lesson's row before completion.
- If the same task also codifies the lesson into `AGENTS.md`, this file, a scoped instruction, a skill, or an agent, remove that corresponding row from `LESSONS_LEARNED.md` instead of keeping a codified duplicate there.
- If no durable lesson emerged, do not force a `LESSONS_LEARNED.md` change.

## Completion Report

- End completed operations with `✅ Outcome`.
- When used, also include `🤖 Agents`, `📘 Instructions`, `🧩 Skills`, and `📦 Other Resources`.
- In each included section, state which resources were used and why they were relevant.
- When `LESSONS_LEARNED.md` was updated, mention it under `📦 Other Resources` with a short reason.
- Omit unused categories instead of adding empty or negative sections.
