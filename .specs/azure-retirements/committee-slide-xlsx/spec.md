# Publish the committee slide artifact as XLSX

Area: Azure Retirement Intelligence  
Status: ready-for-agent

## Problem Statement

The committee receives the slide artifact as TSV and needs an Excel workbook instead. The tabular files used as data should stay in TSV. The monthly export directory currently mixes these files with JSON support artifacts, and the package layout makes report and path changes harder to maintain.

November 2026 is the first monthly bundle to rebuild from an empty output directory. The operator is handling the existing November files; this work must not delete, migrate, or regenerate other months.

## Solution

Publish the slide artifact only as `03_azure_retirements_slide.xlsx`. Preserve the Advisor and Service Health raw artifacts and the aggregate artifact as TSV. Put new JSON and JSONL support artifacts in repository-root `tmp/`, in a component-specific layout that identifies the source or purpose and, where applicable, the month. Keep local replay working with the relocated saved acquisition inputs and manifest. Rename the runtime package directory from `retirements` to `src` without changing the launcher interface.

## User Stories

1. As a committee operator, I want a single XLSX slide artifact, so that I can open the report in Excel without converting a TSV.
2. As a committee reader, I want the existing ordered headings and editorial values, so that the format change does not alter what I review.
3. As a data consumer, I want the Advisor, Service Health, and aggregate TSV contracts to stay the same, so that existing consumers continue to work.
4. As an operator, I want only the requested reports to be published, so that selecting a data-only report does not create a workbook.
5. As an operator, I want support files outside the export directory and identifiable by origin, so that deliverables are easy to find and diagnostics are easy to trace.
6. As an operator, I want to replay from saved local inputs without contacting Azure, so that I can refresh a month's slide artifact on the same checkout.
7. As an editorial operator, I want the committee refresh to publish the XLSX only after the existing approval step, so that routine editorial changes still follow the review workflow.
8. As an operator, I want a failed publication to leave the previous monthly bundle and its replay inputs usable, so that I do not lose a valid publication.
9. As a maintainer, I want the source directory named `src` and report and path rules defined in one place, so that I can change them without updating competing implementations.
10. As a repository contributor, I want November 2026 to start clean without rewriting other months, so that this change does not modify historical deliverables.

## Implementation Decisions

- Replace the slide TSV artifact contract with XLSX. Keep a single source of truth for the slide projection and its ordered headers; write one worksheet with those headers and the projected rows. Preserve text, Unicode, leading zeros, date labels, and blank values without converting source text to numbers, dates, or formulas. A report with no slide rows still produces a valid workbook with its headers.
- Keep raw and aggregate TSV names, headers, and serialization unchanged. For a successful full November publication, the export directory must contain exactly:
  - `01_azure_advisor_retirements_raw.tsv`
  - `01_azure_service_health_advisories_raw.tsv`
  - `02_azure_retirements_aggregate.tsv`
  - `03_azure_retirements_slide.xlsx`
- Keep the existing meaning of the report selectors. A slide-only publication from valid saved inputs publishes just the XLSX in the monthly export directory; data-only selectors publish their corresponding TSVs and no XLSX.
- Centralize destination rules. Keep new source-labelled JSON/JSONL, publication manifests, saved acquisition inputs, and acquisition cache under repository-root `tmp/`. Separate per-month publication support from reusable acquisition cache. Include the source or artifact purpose in the path or filename, and retain existing replay integrity checks. Distinguish separate output destinations so equal months cannot overwrite each other's replay inputs. Keep diagnostics outside exports.
- Preserve whole-month replacement and failure recovery (RET-006). Validate and stage the workbook, TSVs, and month-specific support before replacing a publication. A failed run must not leave an export linked to another generation's support. The cache has a separate lifetime and may be reused or rebuilt; an empty November export directory alone does not invalidate it.
- Preserve the `run.sh` command interface, including selectors, replay and committee refresh options, and existing operator output modes. Resolve a current monthly export directory to its local replay support. Keep the committee sidecar and its editorial semantics unchanged. Update directly coupled contracts, docs, fixtures, and the project-owned editorial workflow to use the XLSX output and revised replay location without removing its explicit approval gate.
- Rename the runtime source directory from `retirements` to `src`; update canonical imports and directly dependent references. Limit additional refactoring to slide projection, artifact format handling, and path ownership. Update the glossary and documented output contract (RET-004). Keep generated outputs out of new commits under RET-003, except intentionally documented sanitized test fixtures.

## Testing Decisions

### Mandatory acceptance checks

| Check | Evidence required |
| --- | --- |
| Full November publication | Run a fixture-backed `all` case for November 2026 with empty destinations. Verify the exact four filenames above, no slide TSV, no support JSON/JSONL under the export root, and source-identifiable support and replay inputs under the repository's `tmp/` layout. |
| Workbook contract | Open the emitted workbook with an XLSX reader. Compare headers, row order, and values with the established slide projection or existing fixture expectations, not with a newly generated TSV. Cover Unicode, blanks, literal formula-like text, and a header-only workbook. |
| Data and selector compatibility | Compare raw and aggregate TSVs with existing expected bytes. Verify that `slides` emits only XLSX and each data-only selector emits its expected TSV without XLSX. |
| Replay and editorial workflow | Replay the fixture-backed monthly export without Azure acquisition. Verify that the manifest resolves relocated inputs and that a missing or altered required input fails explicitly. Verify that explicit committee refresh publishes XLSX with the expected editorial values and that ordinary replay retains its existing behavior. |
| Publication failure and replacement | Inject a failure during a replacement after staging work begins. Check nonzero failure and unchanged prior deliverables and replay support. On success, verify the entire prior monthly publication is replaced without stale artifacts and a different month remains untouched. |
| Rename and launcher | Run the existing v2 pytest suite (`python -m pytest tests/comitato/comitato_azure_retirements_v2`). Verify the canonical import from the renamed package and `run.sh --help` from both the repository root and a different working directory. Check that active docs and the editorial workflow no longer point to a slide TSV. |

### Proposed test seams

Use the existing CLI or orchestration fixture path for the successful publication, selector, and replay checks. Use the existing filesystem publication fault-injection seam for rollback and the existing entrypoint tests for launcher compatibility. Prefer assertions on observable files, content, exit status, and replay behavior over checks on internal writer calls.

### Optional evaluation

A live Azure smoke run for November 2026 is `not-run`. It requires explicit Azure scope and credentials. It is not a substitute for the fixture-backed acceptance checks. No implementation acceptance checks were run while writing this specification.

## Out of Scope

- XLSX versions of Advisor, Service Health, or aggregate data artifacts.
- Backfill, cleanup, or regeneration of other months or deletion of the existing comparison workbook.
- Replay from a fresh clone without the local support files, or migration of historical support bundles.
- Changes to retirement evidence, publication windows, editorial policy, or report selection semantics.
- New PowerPoint output or unrelated code restructuring.

## Further Notes

The operator's November cleanup is separate from implementation. Do not restore or stage those deletions. A clean November output directory is an acceptance setup, not permission to clear cached Azure responses or run live acquisition.
