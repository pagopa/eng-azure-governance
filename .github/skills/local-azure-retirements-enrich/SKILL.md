---
name: local-azure-retirements-enrich
description: "Edit Azure retirement committee notes or apply reviewed notes to an existing monthly slide XLSX. Report generation or a request to run the launcher alone does not activate this skill."
---

# Azure Retirements Committee Enrichment

Save committee editorial changes, present them in chat, and wait for explicit
approval before applying them to an existing monthly slide report.

## Routing

Separate report generation from editorial slide refresh.

- **Generation only:** Run the requested launcher directly. Creating a fresh
  bundle or requesting the slide XLSX as an output is not editorial work.
- **Editorial only:** Use this workflow to edit committee notes or apply
  reviewed notes to an existing monthly slide workbook.
- **Mixed request:** Finish report generation before editorial preflight. Use
  the resulting bundle for the editorial workflow; its approval gate applies
  only to the later slide refresh.

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
- Editorial TSV: `src/comitato/comitato_azure_retirements_v2/data/comitato_editoriale.tsv`.
- Export root: `src/comitato/comitato_azure_retirements_v2/exports`.
- Selected bundle: `<export-root>/<YYYY>/<MM>`.
- Target: `<selected-bundle>/03_azure_retirements_slide.xlsx`.
- Default publication support: `tmp/comitato/comitato_azure_retirements_v2/publications/default/<YYYY>/<MM>`.

For example, `2026 10` selects `exports/2026/10`, never another month.

## Preflight

Inspect the worktree and preserve existing edits. Require the selected monthly
XLSX, its external `publication-manifest.json`, saved acquisition inputs, and editorial YAML. Regenerate the editorial
TSV through the committee YAML adapter whenever the YAML is saved. The manifest must match the
requested year/month, point to integrity-checked saved acquisition inputs, and select
`all` or `slides`. Keep its exact date, selector, scope, and committee window;
do not manufacture a day from the month.

Snapshot the YAML, monthly export, and month-specific support outside the selected directories before editing.
Record the existing artifact names, slide row order, IDs, header, and
non-committee values. Publication replaces the complete monthly bundle:
require export files to match manifest entries whose destination is `exports`;
stop on additional files that replacement would discard. Require support files
to match source-labelled JSONL, the manifest, and saved inputs.

Read the workbook by header name with an XLSX reader and the YAML by
`id_elemento`. Preserve every cell as text. Inspect the whole
YAML for missing or whitespace-only `comitato_descrizione` and
`comitato_retirement_date`; include selected slide IDs in the coverage check.
Require a source-backed YAML entry for each selected ID. For absent IDs,
recover canonical records in memory from the integrity-checked saved inputs,
using the existing normalization and slide projection functions. Use
`src.contracts.committee.merge({}, records)` for source-backed
templates, with the canonical import prefix
`src.comitato.comitato_azure_retirements_v2`.
Insert only absent IDs into the existing YAML; do not replace the document
with the selected month's subset or seed descriptions from flattened workbook
text.
Preparation must not invoke the launcher, `run_config`, `run_replay`, or a
publication store: those entrypoints can write report bundles.

If canonical source data, saved inputs, or required artifacts are unavailable
or incompatible, stop with the exact blocker instead of inventing source data
or silently selecting another month.

## Editorial Rules

Write the committee content in **Italian** for directors who need enough
technical context to recognize the affected service. Use this middle ground:

1. Start with the actual Azure service or technology, then name the affected
   component or version. State what is happening or what to evaluate in direct,
   natural Italian. Do not force a fixed title formula or end with a bare label
   such as `: ritiro`. Match the wording to the event: `sono in ritiro`,
   `accesso disattivato`, or `valutare il passaggio` for an optional improvement.
2. Add one short plain `Suggerimento:` paragraph. Lead with the action and name
   the concrete target when known. Include the main operational impact when it
   helps directors decide. Name a relevant tool, such as Terraform, only when
   it clarifies which work is affected; do not add implementation steps or
   use the suggestion to surface unverified dates or source conflicts.
3. Keep only the description and suggestion in `comitato_descrizione`, without
   Markdown formatting, inline source links, or reference sections. Store
   editorial references separately in `comitato_fonti`, a list of mappings
   with plain-text `titolo` and `url` strings. Preserve every reference title
   and URL, including links that differ from the original `link_fonti`.

Example:

```yaml
comitato_descrizione: >-
  Azure Functions - il supporto per .NET 8 sta terminando


  Suggerimento: pianificare la migrazione delle app a .NET 10 per mantenere
  il supporto, verificando la compatibilità prima della scadenza.
comitato_fonti:
- titolo: Aggiornare Azure Functions | Microsoft Learn
  url: https://learn.microsoft.com/azure/azure-functions/update-language-versions
```

Keep product names, relevant versions, and migration destinations. Explain
unfamiliar abbreviations briefly when needed. Omit implementation procedures,
commands, metric identifiers, package inventories, and configuration recipes.
Avoid vague replacements such as "aggiornare la piattaforma" without naming
what changes. Distinguish a retirement from a performance recommendation.

Fill only empty committee fields, including missing or empty `comitato_fonti`
lists. Keep `comitato_retirement_date` present and set it to an empty string
when the original source description changed or a source-backed entry is new.
Preserve existing non-empty wording, dates, and editorial references unless the
user explicitly requests their revision. New source-backed templates start
with `comitato_fonti: []`; do not overwrite existing references with an empty
template. Preserve meaningful `[SCADUTA]` and `[IMMINENTE]` labels.
Preserve entry IDs, `descrizione_originale_completa`, `link_fonti`,
`retirement_date`, and entries
outside the selected month. Keep folded YAML descriptions and existing layout.

## Dates And Sources

Read the entry's original description, source links, and typed date evidence.
Verify that the source supports the specific service, component or version,
event, and date. Use a retirement, end-of-support, or documented migration
deadline, never an update or notice timestamp. An explicit Service Health date
for a completed change may be used for that event, limited to the affected
instances. For external verification, use official Microsoft sources and send
only public service/version terms or public URLs, never internal inventory data.

Use `MM/DD/YYYY`, or `MM/YYYY` when the source only documents a month. Name
the event and its source and record any newly consulted reference in
`comitato_fonti`. Use `[SCADUTA]` only for a deadline that has already passed
as of execution; do not label a completed change as an expired deadline.

When dates conflict for the same event, use a single deadline only if a
checked, service-specific Microsoft source establishes the action and scope.
For example, state `Entro il 03/15/2027 — Migrare a WAF Policy` when the product
guide establishes that migration deadline, not both the guide and Advisor dates.
Do not promote an Advisor-only candidate or add a day that the source does not
document. If no usable date can be verified, write only
`Consultare la documentazione Microsoft.` in `comitato_retirement_date`.
For an optional recommendation with no retirement event, use `Non applicabile`.
Do not include candidate dates, `da confermare`, or verification notes in
either management field. Preserve the original source metadata and explain
material omissions separately in the technical review.

## Save And Review The YAML

Save the enriched YAML before reporting changes. Validate parsing, unique keys,
selected-ID coverage, and a non-empty `comitato_descrizione`. Validate that
each date field being enriched is a string with verified dates at source
precision, the generic documentation pointer, or a not-applicable statement,
as appropriate. Newly initialized entries may start with an empty date before
enrichment.
Validate plain-text editorial wording and the separate `comitato_fonti` list
of `{titolo, url}` mappings. Regenerate the sibling editorial TSV through
`src.adapters.filesystem.committee_yaml.write_tsv` after every save;
encode nested references and dates as compact JSON in that sidecar. Selective
editorial edits must preserve the existing YAML layout. Full programmatic
document generation may use `committee_yaml.write`, which writes both files.
These editorial references do not add columns to the monthly slide XLSX.
Compare source descriptions with the canonical replay data: the existing merge
deliberately clears editorial descriptions, dates, and references when the
original has changed. Workbook values retain tabs and line breaks; compare
them to the canonical values rather than flattening.

Compare the saved YAML with its snapshot and present the actual changes using
the [editorial review template](references/chat-templates.md#editorial-review).
Include the selected month, distinct changed-entry and field counts, affected
services, before/after highlights, reasons for material date omissions in a
separate technical note, validation results, and file links. State clearly that
the editorial YAML and editorial TSV are saved but the selected monthly slide
XLSX is unchanged.
Record the exact reviewed YAML, editorial TSV, and source manifest state for the
approval check.
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

  During the editorial stage, do not run the launcher, publication entrypoints,
  or any report-writing script before approval, even against a temporary output
  root. A pending or declined review must leave all exports and monthly support
  files unchanged by that stage.
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
root. Replay resolves the source bundle to its original support directory.
Do not copy just the XLSX back: the launcher must publish its consistent
manifest, saved inputs, and complete report bundle.

## Verification And Completion

Require exit status zero and JSON `status: published`. Then verify:

- Only the requested monthly bundle was republished.
- All prior report artifacts remain; non-slide reports are byte-identical.
- Slide header, row order, IDs, and every column except
  `comitato_descrizione` and `comitato_retirement_date` match the snapshot.
- Both committee cells match the YAML for every selected row, preserving
  tabs, carriage returns, and newlines as workbook text.
- Only source-backed new entries, previously empty committee fields, or
  explicitly requested revisions changed in YAML; all existing original
  metadata and unrelated entries remain intact.

If a check fails, report failure and the affected IDs; do not claim a partial
refresh as success. Keep the snapshot available for recovery and never revert
unrelated user edits. Remove task-owned temporary outputs after success.

Use the [publication result template](references/chat-templates.md#publication-result)
only after these checks pass. Note material date omissions separately from
published wording and link the YAML and target XLSX. On failure, identify the
failed stage and actual file state instead of displaying the success template.
Do not commit unless requested.

## Evaluation

The bundled [evaluation pack](tests/evaluation/evals.json) covers missing inputs,
editorial balance, source/date handling, review UX, approval gating,
preservation, and safe publication.
Its case specifications are not evidence of executed model evaluations.
