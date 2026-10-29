---
name: local-azure-retirements-enrich
description: "Use when enriching Azure retirement committee YAML with director-friendly, service-first Italian wording, presenting the saved changes for review, and refreshing the selected month's slide TSV through run.sh only after explicit user approval."
---

# Azure Retirements Committee Enrichment

Save committee editorial changes, present them in chat, and wait for explicit
approval before applying them to an existing monthly slide report. This
workflow does not acquire Azure data or generate a new retirement inventory.

## Inputs

The only data inputs are **year and month**; publication requires a separate
approval after the saved YAML changes are presented. Reuse an explicit year/month in
the request; otherwise ask for the missing values together in one form and
wait. Never treat an example, an empty reply, or the current date as a selection.
Accept a four-digit year and a month from 1 to 12; normalize the month to two
digits. Do not ask for editorial style, technical choices, or file paths.

Resolve these paths from the repository root:

- Launcher: `src/comitato/comitato_azure_retirements_v2/run.sh`.
- Editorial YAML: `src/comitato/comitato_azure_retirements_v2/data/comitato_editoriale.yaml`.
- Export root: `src/comitato/comitato_azure_retirements_v2/exports`.
- Selected bundle: `<export-root>/<YYYY>/<MM>`.
- Target: `<selected-bundle>/03_azure_retirements_slide.tsv`.

For example, `2026 10` selects `exports/2026/10`, never another month.

## Preflight

Inspect the worktree and preserve existing edits. Require the selected TSV,
`publication-manifest.json`, and editorial YAML. The manifest must match the
requested year/month, contain integrity-checked `saved_inputs`, and select
`all` or `slides`. Keep its exact date, selector, scope, and committee window;
do not manufacture a day from the month.

Snapshot the YAML and monthly files outside the selected bundle before editing.
Record the existing artifact names, slide row order, IDs, header, and
non-committee values. Publication replaces the complete monthly bundle:
require its files to match the manifest's artifact list plus the manifest;
stop on additional files that replacement would discard.

Read the TSV by column name and the YAML by `id_elemento`. Inspect the whole
YAML for missing or whitespace-only `comitato_descrizione` and
`comitato_retirement_date`; include selected slide IDs in the coverage check.
Require a source-backed YAML entry for each selected ID. For absent IDs,
recover canonical records in memory from the integrity-checked saved inputs,
using the existing normalization and slide projection functions. Use
`retirements.contracts.committee.merge({}, records)` for source-backed
templates, with the canonical import prefix
`src.comitato.comitato_azure_retirements_v2`.
Insert only absent IDs into the existing YAML; do not replace the document
with the selected month's subset or seed descriptions from flattened TSV.
Preparation must not invoke the launcher, `run_config`, `run_replay`, or a
publication store: those entrypoints can write report bundles.

If canonical source data, saved inputs, or required artifacts are unavailable
or incompatible, stop with the exact blocker instead of inventing source data
or silently selecting another month.

## Editorial Rules

Write the committee content in **Italian** for directors who need enough
technical context to recognize the affected service. Use this middle ground:

1. Start with a bold title: **service - affected component/version: change**.
   Name the actual Azure service or technology before describing the event.
2. Add one short **Suggerimento:** paragraph with the migration or action,
   its concrete target when known, and the main operational impact.
3. Keep the relevant source links in Markdown after the suggestion.

Example:

```text
**Azure Functions - .NET 8: fine del supporto**

**Suggerimento:** pianificare la migrazione delle app a .NET 10 per mantenere
il supporto, verificando la compatibilità prima della scadenza.

[Aggiornare Azure Functions | Microsoft Learn](https://learn.microsoft.com/azure/azure-functions/update-language-versions)
```

Keep product names, relevant versions, and migration destinations. Explain
unfamiliar abbreviations briefly when needed. Omit implementation procedures,
commands, metric identifiers, package inventories, and configuration recipes.
Avoid vague replacements such as "aggiornare la piattaforma" without naming
what changes. Distinguish a retirement from a performance recommendation.

Fill only empty committee fields. Preserve existing non-empty wording and
dates unless the user explicitly requests their revision. Preserve entry IDs,
`descrizione_originale_completa`, `link_fonti`, `retirement_date`, and entries
outside the selected month. Keep folded YAML descriptions and existing layout.

## Dates And Sources

Read the entry's original description, source links, and typed date evidence.
Use retirement or end-of-support dates, never an update timestamp.
Prefer official Microsoft sources for any external verification; send only
public service/version terms or public URLs, never internal inventory data.

Use the existing `MM/DD/YYYY` display convention, with the event and source.
If only a month is documented, retain month-level precision. Label past dates
`[SCADUTA]` using the execution date. Show conflicting Advisor/documentation
dates separately, without silently choosing one. Do not invent a deadline for
an undated recommendation.

An Advisor-only date is acceptable when explicitly attributed to Azure Advisor
and marked "data da confermare nella fonte collegata". Do not claim that a
linked page verifies a date unless it was actually checked. Preserve source
metadata even when documentation reports a different operational deadline.

## Save And Review The YAML

Save the enriched YAML before reporting changes. Validate parsing, unique keys,
selected-ID coverage, and non-empty strings in both committee fields. Compare source
descriptions with the canonical replay data: the existing merge deliberately
clears editorial descriptions when the original has changed. A TSV flattens
tabs and line breaks to spaces; that formatting alone is not a source change.

Compare the saved YAML with its snapshot and present the actual changes using
the [editorial review template](references/chat-templates.md#editorial-review).
Include the selected month, distinct changed-entry and field counts, affected
services, before/after highlights, date/source uncertainty, validation results,
and file links. State clearly that the YAML is saved but the TSV is unchanged.
Record the exact reviewed YAML and source manifest state for the approval check.
If there are no edits, report that honestly; a no-op is not publication consent.

## Approval Gate

After the summary, use `ask_user` with the choices defined in the
[approval form](references/chat-templates.md#approval-form), then wait.
Only a clear affirmative reply to this specific review authorizes the launcher
for the presented YAML and selected month. Supplying year/month, approving
editorial wording earlier, or asking generally to refresh is not this approval.

- **Approve:** continue only with the recorded review state.
- **Request changes:** revise the YAML, validate it, present a fresh summary,
  and request approval again.
- **Decline:** retain the saved YAML and report that slide publication was skipped.
- **Skipped, empty, unavailable, timed-out, or ambiguous reply:** leave approval
  pending and stop. Never choose a default or treat silence as consent.

Until approval, do not run the launcher, publication entrypoints, or any
report-writing script, even against a temporary output root. A pending or
declined review must leave all TSVs and monthly manifests unchanged.
If the YAML, selected month, or source bundle changes after review, invalidate
the approval and present the new changes for approval before execution.
Do not mark an approval-pending workflow as fully published.

## Refresh Through The Launcher

After approval, confirm the reviewed YAML and source manifest are unchanged.
Run from the repository root, substituting only the approved year/month:

```bash
bash src/comitato/comitato_azure_retirements_v2/run.sh \
  --replay-bundle "src/comitato/comitato_azure_retirements_v2/exports/<YYYY>/<MM>" \
  --refresh-committee \
  --committee-yaml src/comitato/comitato_azure_retirements_v2/data/comitato_editoriale.yaml \
  --output-path src/comitato/comitato_azure_retirements_v2/exports \
  --output-format json \
  --no-debug-log
```

This explicit replay mode performs no Azure acquisition, retains the saved
monthly selection, and does not rewrite the YAML. Do not substitute
`--report slides` in a live run: it could replace the month with a smaller
artifact set. Never fall back to live execution when replay fails. Surface
dependency, integrity, schema, publication, and source-mismatch errors.

For a safe pre-publication check, first run the same command with
`--output-path` pointing to an isolated temporary export root. Verify the
candidate against the snapshot before running it against the real export
root. Do not copy just the TSV back: the launcher must publish its consistent
manifest and complete report bundle.

## Verification And Completion

Require exit status zero and JSON `status: published`. Then verify:

- Only the requested monthly bundle was republished.
- All prior report artifacts remain; non-slide reports are byte-identical.
- Slide header, row order, IDs, and every column except
  `comitato_descrizione` and `comitato_retirement_date` match the snapshot.
- Both committee cells match the YAML for every selected row, using the
  existing TSV rule: replace each tab, carriage return, and newline with a
  space. Do not collapse all whitespace or compare multiline YAML literally.
- Only source-backed new entries, previously empty committee fields, or
  explicitly requested revisions changed in YAML; all existing original
  metadata and unrelated entries remain intact.

If a check fails, report failure and the affected IDs; do not claim a partial
refresh as success. Keep the snapshot available for recovery and never revert
unrelated user edits. Remove task-owned temporary outputs after success.

Use the [publication result template](references/chat-templates.md#publication-result)
only after these checks pass. Include source/date uncertainty and link the YAML
and target TSV. On failure, identify the failed stage and actual file state
instead of displaying the success template. Do not commit unless requested.

## Evaluation

The bundled [evaluation pack](tests/evaluation/evals.json) covers missing inputs,
editorial balance, source/date handling, review UX, approval gating,
preservation, and safe publication.
Its case specifications are not evidence of executed model evaluations.
