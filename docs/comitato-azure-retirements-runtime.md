# Comitato Azure Retirements Runtime Notes

## Purpose

This document describes runtime behavior for `src/comitato/comitato_azure_retirements/comitato-azure-retirements.py`, including parallel collectors and troubleshooting artifacts.

## Workflow Selection

The runtime supports stage selection through `--workflow` (or `AZURE_RETIREMENTS_WORKFLOW`):

- `raw`: produce source Advisor and Service Health TSV files.
- `aggregate`: merge and group source rows into a normalized aggregate contract.
- `slide`: project aggregate rows into the committee-facing subset.
- `full`: shorthand for `raw,aggregate,slide`.

When `--mode schema-only` is used, the `raw` stage is valid and writes header-only artifacts without requiring live or fixture rows.

When `aggregate` runs without `raw`, the runtime reuses existing raw files for the selected month.
When `slide` runs without `aggregate`, the runtime reuses the existing aggregate file for the selected month.

## Runtime Artifacts

The exporter writes these required TSV files:

- `src/comitato/comitato_azure_retirements/exports/YYYY/MM/01_azure_advisor_retirements_raw.tsv`
- `src/comitato/comitato_azure_retirements/exports/YYYY/MM/01_azure_service_health_advisories_raw.tsv`
- `src/comitato/comitato_azure_retirements/exports/YYYY/MM/02_azure_retirements_aggregate.tsv`
- `src/comitato/comitato_azure_retirements/exports/YYYY/MM/03_azure_retirements_slide.tsv`
- `tmp/comitato/comitato_azure_retirements/run/YYYY/MM/azure_retirements_run_diagnostics.tsv`

Generated-data policy:

- Files under `src/comitato/comitato_azure_retirements/exports/` are runtime outputs and are ignored by Git.
- Keep this path untracked; use `--output-root tmp/comitato/...` for local review snapshots.
- If a tracked fixture is required, sanitize it first and document the reason in the related plan or PR notes.

Compatibility fallback: when aggregate/slide workflows run without raw, the runtime can still reuse legacy raw filenames
(`azure_advisor_retirements_aggregate.tsv` and `azure_service_health_advisories_aggregate.tsv`) if they are present.

The runtime directory also contains:

- `tmp/comitato/comitato_azure_retirements/run/YYYY/MM/azure_retirements_run_manifest.json`
- `tmp/comitato/comitato_azure_retirements/run/YYYY/MM/<run_id>_debug.log`

## Service Health Normalization Rules

Service Health rows follow this precedence for `date_for_window`:

1. Explicit retirement or deprecation deadlines parsed from advisory text (title, summary, actions, description).
2. `impactMitigationTime`.
3. `impactStartTime`.
4. `lastUpdateTime`.

Impacted service and region values preserve the source `impact` item pairing. The runtime must not fabricate
cross-product combinations that do not exist in the source event shape.

## Parallel Collection

`live` mode collects subscription-scoped data concurrently for:

- Advisor recommendations
- Service Health events

Worker count selection:

- CLI override: `--max-workers <N>`
- Environment override: `AZURE_RETIREMENTS_MAX_WORKERS=<N>`
- Default when unset: `min(16, number_of_resolved_subscriptions)`

Safety behavior:

- In strict mode (`--allow-degraded` not set), one subscription failure fails the run.
- In degraded mode (`--allow-degraded` set), subscription failures are recorded in diagnostics and collection continues.

Manifest behavior:

- `azure_retirements_run_manifest.json` sets `degraded_mode: true` when degraded evidence is present
  (`advisor_subscription_failures`, `service_health_subscription_failures`, or `resource_graph_truncated`),
  even when those diagnostics are warnings.

## Debug Log Contract

`<run_id>_debug.log` is JSON Lines, one event per line. Each exporter run writes its own debug log and prints the path during artifact writing.

Core fields:

- `timestamp_utc`: UTC timestamp in ISO-8601 `Z` format
- `severity`: `info`, `warning`, or `error`
- `event`: stable event identifier for filtering
- `message`: operator-facing message
- `run_id`: runtime correlation id
- `thread`: Python thread name
- `context`: structured event details

## Problem Determination Workflow

1. Run the exporter in `schema-only`, `fixture`, or `live` mode.
2. Check `azure_retirements_run_diagnostics.tsv` for failed checks and required actions.
3. Filter `azure_retirements_debug.log` by `run_id` and inspect event timeline.
4. Correlate diagnostics failures with debug events for the same subscription or collector.
5. Tune worker count if retries or throttling increase.

Useful debug events for artifact checks:

- `advisor_report_written`: Advisor TSV path and row count.
- `service_health_report_written`: Service Health TSV path and row count.
- `diagnostics_written`: diagnostics TSV path and row count.
- `run_manifest_written`: manifest path.

Example commands:

```bash
bash src/comitato/comitato_azure_retirements/run.sh --mode schema-only
bash src/comitato/comitato_azure_retirements/run.sh --mode live --max-workers 8 --allow-degraded
```

## Validation Commands

Use these focused checks before closeout:

```bash
src/comitato/comitato_azure_retirements/.venv/bin/python -m compileall -q src/comitato/comitato_azure_retirements tests/comitato/comitato_azure_retirements
src/comitato/comitato_azure_retirements/.venv/bin/python -m pytest -q tests/comitato/comitato_azure_retirements
bash -n src/comitato/comitato_azure_retirements/run.sh
shellcheck -s bash src/comitato/comitato_azure_retirements/run.sh
bash src/comitato/comitato_azure_retirements/run.sh --mode schema-only --output-root tmp/comitato/review-schema-only-output
git diff --check origin/main...HEAD
```
