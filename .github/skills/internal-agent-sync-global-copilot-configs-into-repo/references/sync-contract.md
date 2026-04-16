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
- `.github/workflows/terraform-pre-commit.yml`
- `.github/agents/**`
- `.github/instructions/**`
- `.github/skills/**`, including bundled `references/`, `assets/`, `scripts/`, `agents/`, and licenses

Do not sync `README.md`, changelogs, other workflows, templates, or bootstrap helpers unless the user explicitly expands scope.
Do not sync consumer-facing resources whose file or directory name starts with `internal-sync-`; those remain source-only operational controls for the standards repository.
Treat `LESSONS_LEARNED.md` as a structure-managed exception: sync the source template and contract, but preserve target-authored pending lesson rows instead of copying source rows into consumer repositories.

## Target Rules

- Preserve target `local-*` assets under mirrored categories and surface them in the plan or final report.
- Preserve target `.github/local-copilot-overrides.md` as a consumer-owned local exception layer and surface it in the plan or final report when present.
- Delete target-owned non-`local-*` assets inside mirrored categories during `apply`.
- Do not mirror a source `.github/local-copilot-overrides.md` into consumer repositories.
- Keep the target target-agnostic. The default assumptions are only `.github/` and root `AGENTS.md`.
- Ensure target root `LESSONS_LEARNED.md` exists. If it already exists, align it to the current source structure and migrate preserved pending lesson rows when the source table shape changes.
- Ensure the target root `.gitignore` contains an ignore entry for `tmp/superpowers/`.
- Treat the `.gitignore` update as target-local hygiene: ensure the required ignore entry exists without mirroring the source repository `.gitignore`.

## Root Guidance Ownership

When root guidance is in scope, keep the target files in these roles:

- `AGENTS.md`: strategic bridge, precedence anchor, naming contract, and cross-surface routing guidance
- `LESSONS_LEARNED.md`: retained-learning ledger template aligned from source structure while preserving target-authored pending lessons; it remains non-canonical and repo-local in content
- `.github/copilot-instructions.md`: repo-wide GitHub Copilot projection
- `.github/local-copilot-overrides.md`: consumer-local exception layer authorized by `AGENTS.md`; it may override synced defaults only when conflict, scope, reason, and disclosure are explicit
- `.github/INVENTORY.md`: exact live catalog generated from target filesystem state

Do not flatten these roles into one file. Do not let target `AGENTS.md` become an inventory dump or a second full copy of `.github/copilot-instructions.md`. Do not let `.github/local-copilot-overrides.md` replace the bridge or catalog roles.

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

## Reporting Contract

Completed runs should make these facts visible:

- target analysis and selected mode
- root-guidance alignment strategy and `LESSONS_LEARNED.md` status
- preserved `local-*` assets and `.github/local-copilot-overrides.md` status
- target-only cleanup decisions
- plan-file status and lifecycle
- validation results and remaining blockers

End completed runs with `✅ Outcome`.
Include `🤖 Agents`, `📘 Instructions`, `📝 Prompts`, `🧩 Skills`, and `📦 Other Resources` only when those categories were actually used, and state why each listed resource mattered.
