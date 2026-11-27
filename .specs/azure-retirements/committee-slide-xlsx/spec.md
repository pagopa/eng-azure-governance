# Publish the Azure retirements committee workbook

## Goal

Give the committee a workbook it can open directly in Excel. Keep the TSV
feeds unchanged and keep replay files out of the export. The runtime lives
under `src`; `run.sh` remains the operator entrypoint.

## Output contract

`all` replaces the selected month with exactly these deliverables:

| File | Contract |
| --- | --- |
| `01_azure_advisor_retirements_raw.tsv` | Existing Advisor TSV, unchanged |
| `01_azure_service_health_advisories_raw.tsv` | Existing Service Health TSV, unchanged |
| `02_azure_retirements_aggregate.tsv` | Existing aggregate TSV, unchanged |
| `03_azure_retirements_slide.xlsx` | One worksheet with the existing slide headers, row order, and editorial values |

`slides` publishes only the workbook. Each data-only selector publishes only
its TSV. Upstream dependencies do not add deliverables. Do not publish a slide
TSV. Workbook values retain the existing text and blanks, including Unicode,
leading zeros, date labels, and formula-like text as literal text. An empty
report still has its header row.

## Publish and replay

- Keep source JSONL, the manifest, and saved acquisition inputs under the
  component's repository-root `tmp/` directory, separated by export destination
  and month. Keep reusable acquisition cache separate from monthly support.
- Stage each file directly on the filesystem that will receive it. Reread and
  validate the staged payloads and build the manifest from those bytes before
  replacing either directory. Replace the whole month; if publication fails,
  restore both the previous export and its matching replay support (RET-006).
- Resolve replay from the source month's export or support directory, even
  when writing to a different output root. Verify saved inputs before use;
  missing or altered inputs fail without contacting Azure. During replay,
  apply the current editorial YAML only on explicit committee refresh. The
  editorial workflow still requires approval before running the refresh.

Keep one slide projection and header definition, one destination rule, and
one staging and replacement flow for both directories. Reuse the existing
report contracts and workbook library; do not add report-specific publishers
or change acquisition, editorial rules, selectors, or operator output modes.

## Acceptance

Run `make test-v2` and use the existing fixtures to verify:

- A clean November 2026 `all` run produces the four listed files, with the
  expected TSV bytes and support files outside exports. Verify each selector.
- An XLSX reader confirms the header and row order, text and blank values,
  literal formula-like text, and a header-only workbook.
- Offline replay works from the export path and rejects missing or altered
  inputs. Explicit refresh applies the editorial values; ordinary replay
  keeps its existing behavior.
- A failed replacement leaves the previous export and replay support intact.
  Successful replacement removes stale files for that month only. Staging does
  not require cross-filesystem renames between exports and support.
- The documented import and `run.sh --help` work from the repository root and
  another working directory.

November cleanup belongs to the operator. Do not restore or stage existing
deletions, clear the cache, regenerate other months, or run live Azure
acquisition as part of acceptance. Keep generated outputs out of commits
(RET-003) and keep the documented artifact contract current (RET-004).
