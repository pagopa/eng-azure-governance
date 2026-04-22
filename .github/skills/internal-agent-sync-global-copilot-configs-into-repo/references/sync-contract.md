# Sync Contract

Use this reference when the paired agent or this skill needs the exact sync rules instead of the compact workflow summary.

## Source-Managed Scope

Mirror or structurally align these source-managed paths into the consumer repository:

- `AGENTS.md`
- `LESSONS_LEARNED.md`
- `.editorconfig`
- `.pre-commit-config.yaml`
- `.github/copilot-instructions.md`
- `.github/copilot-code-review-instructions.md`
- `.github/copilot-commit-message-instructions.md`
- `.github/security-baseline.md`
- `.github/DEPRECATION.md`
- `.github/repo-profiles.yml`
- `.github/workflows/_pre-commit.yml`
- `.github/agents/**`
- `.github/instructions/**`
- `.github/skills/**`, including bundled `references/`, `assets/`, `scripts/`, `agents/`, and licenses

Do not sync `README.md`, changelogs, other workflows, templates, or bootstrap helpers unless the user explicitly expands scope.
Do not sync consumer-facing resources whose file or directory name starts with `internal-sync-`; those remain source-only operational controls for the standards repository.
Treat `LESSONS_LEARNED.md` as a structure-managed exception: sync the source template and contract, but preserve target-authored pending lesson rows instead of copying source rows into consumer repositories.
When a consumer-local creator depends on shared runtime-critical rules, keep a self-contained mirror of those rules inside the creator bundle and track the mirror path in the source inventory plus the target `.github/copilot-sync.manifest.json`; do not assume cross-bundle references or target-local extras will be present at runtime.

## Target Rules

- Preserve target `local-*` assets under mirrored categories and surface them in the plan or final report.
- Materialize `.github/copilot-instructions.override.md.template` from the standards repository into the consumer-local copilot instructions override file when that target file is missing, then preserve the target file as a consumer-owned local exception layer and surface it in the plan or final report when present.
- Delete target-owned non-`local-*` assets inside mirrored categories during `apply`.
- Keep the target target-agnostic. The default assumptions are only `.github/` and root `AGENTS.md`.
- Ensure target root `LESSONS_LEARNED.md` exists. If it already exists, align it to the current source structure and migrate preserved pending lesson rows when the source table shape changes.
- Ensure the target root `.gitignore` contains an ignore entry for `tmp/superpowers/`.
- Treat the `.gitignore` update as target-local hygiene: ensure the required ignore entry exists without mirroring the source repository `.gitignore`.

## Root Guidance Ownership

When root guidance is in scope, keep the target files in these roles:

- `AGENTS.md`: strategic bridge, precedence anchor, naming contract, and cross-surface routing guidance
- `LESSONS_LEARNED.md`: retained-learning ledger template aligned from source structure while preserving target-authored pending lessons; it remains non-canonical and repo-local in content
- `.github/copilot-instructions.md`: repo-wide GitHub Copilot projection
- the consumer-local GitHub instructions overrides file: consumer-local exception layer authorized by `AGENTS.md`; it may override synced defaults only when conflict, scope, reason, and disclosure are explicit
- `.github/INVENTORY.md`: exact live catalog generated from target filesystem state

Do not flatten these roles into one file. Do not let target `AGENTS.md` become an inventory dump or a second full copy of `.github/copilot-instructions.md`. Do not let the consumer-local GitHub instructions overrides file replace the bridge or catalog roles.

## Tracking Plan Lifecycle

- Write `tmp/copilot-sync.plan.md` before any mirrored change.
- Keep the plan in the target repository so the user can inspect pending sync work between runs.
- A follow-up `apply` against the same target therefore needs `--allow-dirty-target` when `tmp/copilot-sync.plan.md` is the only target diff left by `plan`; do not use that flag to bypass unrelated dirty target changes.
- When `apply` finishes and nothing remains pending, remove the plan file.
- If `apply` stops early or manual follow-up remains, keep the plan file for the next run.
- Remove legacy tracking artifacts named `internal-sync-*` from the target during `apply`.

## Automation Entry Points

- Preferred wrapper: `.github/scripts/sync_copilot_catalog.sh`
- Audit wrapper: `.github/scripts/audit_copilot_catalog.sh`
- Python entry point: `.github/scripts/sync_copilot_catalog.py`
- Audit entry point: `.github/scripts/audit_copilot_catalog.py`
- Core implementation: `.github/scripts/lib/syncing.py`
- Target manifest: `.github/copilot-sync.manifest.json`

Prefer the shipped scripts when the request matches `plan`, `apply`, or a script-backed audit flow. Fall back to manual reasoning only when the request goes beyond the current automation contract.

## Validation Sequence

Use the closest existing checks for the touched behavior:

1. `./.github/scripts/check_catalog_consistency.sh --root . --include-token-risks`
2. `./.github/scripts/build_inventory.sh --root .`
3. `./.github/scripts/sync_copilot_catalog.sh plan --target-repo <repo>`
4. `./.github/scripts/audit_copilot_catalog.sh --root .` when the decision depends on governance drift or local override behavior
5. `pytest tests/test_sync_and_token_risks.py` when sync automation changes

If a dedicated contract test is missing, call out the gap explicitly.

After `apply`, run the closest target-local catalog or contract validation when preserved `local-*` assets, preserved consumer-local GitHub instructions overrides, or other target-owned assets can still expose latent drift. Treat any resulting fixes as consumer-local follow-up work, not as source-baseline drift, unless the same finding reproduces against the source-managed assets themselves.

## Reporting Contract

Completed runs should make these facts visible:

- target analysis and selected mode
- root-guidance alignment strategy and `LESSONS_LEARNED.md` status
- preserved `local-*` assets and consumer-local GitHub instructions overrides status
- target-only cleanup decisions
- plan-file status and lifecycle
- validation results and remaining blockers

End completed runs with `✅ Outcome`.
Keep `✅ Outcome` concise by default.
When additional provenance or execution detail would help, offer it as optional follow-up detail with a compact prompt that accepts number-only replies.
Include `🤖 Agents`, `📘 Instructions`, `📝 Prompts`, `🧩 Skills`, and `📦 Other Resources` only when those categories were actually used and the user asked for the detail, or when a narrower scoped contract requires inline disclosure.
State why each listed resource mattered in any included detail section.
