# Comitato Azure Retirements Runtime Notes

## Purpose

This document describes runtime behavior for `src/comitato/comitato_azure_retirements/comitato-azure-retirements.py`, including parallel collectors and troubleshooting artifacts.

## Runtime Artifacts

The exporter writes these required TSV files:

- `src/comitato/comitato_azure_retirements/exports/YYYY/MM/azure_advisor_service_retirements_raw.tsv`
- `src/comitato/comitato_azure_retirements/exports/YYYY/MM/azure_service_health_advisories_raw.tsv`
- `tmp/comitato/comitato_azure_retirements/run/YYYY/MM/azure_retirements_run_diagnostics.tsv`

The runtime directory also contains:

- `tmp/comitato/comitato_azure_retirements/run/YYYY/MM/azure_retirements_run_manifest.json`
- `tmp/comitato/comitato_azure_retirements/run/YYYY/MM/<run_id>_debug.log`

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
