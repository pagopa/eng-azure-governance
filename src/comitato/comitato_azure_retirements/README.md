# Comitato Azure Retirements Export

## Purpose

This toolkit exports Azure retirements evidence for committee review.

Persisted outputs currently include:

- `01_azure_advisor_retirements_raw.tsv`
- `01_azure_service_health_advisories_raw.tsv`
- `02_azure_retirements_aggregate.tsv`
- `03_azure_retirements_slide.tsv`
- `azure_retirements_run_diagnostics.tsv`
- `azure_retirements_run_manifest.json`

## Non-Purpose

This project does not:

- Build PowerPoint slides.
- Produce a final executive merged table.
- Automate portal interactions.
- Infer resource-level impact for Service Health from names, regions, service labels,
  or other non-authoritative similarity.

## Dependency Decision Note

- Candidates compared:
  - Python standard library (`urllib`, `subprocess`, `csv`, `json`) with `az` CLI token acquisition.
  - `requests` plus `urllib3` retry handling and `rich` console rendering.
  - `httpx` plus `tenacity` and `rich`.
  - Azure management SDK packages.
- Final choice: `requests`, `urllib3`, and `rich`, while keeping `az` CLI token acquisition.
- Current aggregate implementation keeps `pandas` for grouping stability, isolated behind a single helper for future replacement.
- Why: this keeps the authentication path explicit, adds robust retry handling for `429` and transient `5xx` responses, and produces clean sectioned console logs with emoji and readable summaries while preserving committee output consistency.

## Python Version

The launcher enforces the exact interpreter version declared in the repository `.python-version` file (`3.13.9`).

- Default interpreter: `python3`
- Optional override: set `PYTHON_BIN` to another executable path only if it resolves to the same `3.13.9` version.

## Required Runtime Access

For `--mode live`, the caller needs:

- Azure access to target subscriptions or management groups.
- Read access for Advisor recommendations.
- Read access for Resource Graph.
- Read access for Resource Health events.

## Modes

- `schema-only`: writes advisor headers, diagnostics, and manifest with no live Azure calls.
- `fixture`: reads JSON fixtures from `--fixture-dir`.
- `live`: queries Azure APIs.

## Scope Inputs

Use one or both:

- `--subscriptions "sub1,sub2"`
- `--management-groups "mg1,mg2"`

Live mode refuses to run with empty scope.

## CLI

The Bash launcher bootstraps a local `.venv` and installs the hash-locked dependencies from `requirements.txt` before execution.

```bash
bash src/comitato/comitato_azure_retirements/run.sh --help
python3 src/comitato/comitato_azure_retirements/comitato-azure-retirements.py --help
```

Example schema-only run:

```bash
bash src/comitato/comitato_azure_retirements/run.sh --mode schema-only
```

Example live run:

```bash
bash src/comitato/comitato_azure_retirements/run.sh \
  --mode live \
  --subscriptions "00000000-0000-0000-0000-000000000000" \
  --as-of-date 2026-06-18 \
  --health-query-start 2025-01-01
```

## Runtime Output

- Console execution is split into sections for authentication, scope resolution, data collection, artifact writing, and final summary.
- Operator-facing logs use emoji markers to highlight progress, warnings, retries, and terminal failures.
- Persistent logs use human-readable text, UTC timestamps, stable event names, and contextual `key=value` fields.
- Unhandled failures record the active workflow stage, exception type, complete traceback, and chained causes.
- When `--verbose` is enabled, the exporter also prints per-subscription page counts and management group resolution details.

## Runtime Configuration

`config/azure_rel.conf` is the single configuration file for the allowed Azure
regions and logging behavior:

```ini
[regions]
allowed =
    italynorth
    westeurope
    global

[logging]
enabled = true
level = INFO
console_level = INFO
include_traceback = true
log_directory =
```

- `level` controls the persistent file threshold.
- `console_level` controls the operator console threshold.
- Supported levels are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`.
- An empty `log_directory` uses the standard runtime directory under `tmp/`.
- A relative `log_directory` is resolved from the directory containing
  `azure_rel.conf`.
- Configuration errors stop startup with an explicit missing section, invalid
  value, or missing file message.

`azure_rel.conf` replaces the former `azure_regions.conf`; there is no legacy
fallback.

## Environment Variables

CLI flags override environment values.

- `AZURE_SUBSCRIPTIONS`
- `AZURE_MANAGEMENT_GROUPS`
- `AZURE_RETIREMENTS_OUTPUT_ROOT`
- `AZURE_RETIREMENTS_AS_OF_DATE`
- `AZURE_HEALTH_QUERY_START`
- `AZURE_RETIREMENTS_FIXTURE_DIR`
- `AZURE_RETIREMENTS_ALLOW_DEGRADED`
- `AZURE_BEARER_TOKEN` (optional explicit bearer token; otherwise `az` CLI token is used)

`AZURE_RETIREMENTS_OUTPUT_ROOT` controls export artifacts (raw Advisor TSV, raw Service Health TSV, aggregate TSV, slide TSV, and optional raw JSONL traces). Runtime diagnostics and manifest files are always written under `tmp/`.

## Output Path

Export artifacts are written under:

```text
src/comitato/comitato_azure_retirements/exports/YYYY/MM/
```

Runtime diagnostics are written under:

```text
tmp/comitato/comitato_azure_retirements/run/YYYY/MM/
```

These paths are runtime artifacts and are intentionally Git-ignored.

Required export files:

- `01_azure_advisor_retirements_raw.tsv`
- `01_azure_service_health_advisories_raw.tsv`
- `02_azure_retirements_aggregate.tsv`
- `03_azure_retirements_slide.tsv`

Required runtime files:

- `azure_retirements_run_diagnostics.tsv`
- `azure_retirements_run_manifest.json`
- `YYYYMMDDHHMM_azure-retirements-<run-id>_debug.log` when
  `logging.enabled=true`

The filename timestamp is UTC. Each text log line also starts with an ISO UTC
timestamp. When a run fails, the terminal message identifies the failing stage
and points to the log containing the complete traceback.

Optional export files with `--write-raw-jsonl`:

- `azure_advisor_retirements_raw.jsonl`
- `azure_service_health_advisories_raw.jsonl`

Publication selection uses the inclusive calendar window
`as_of_date <= publication_date <= add_calendar_months(as_of_date, 12)`.
Advisor publication dates come from `retirement_date` and only current Advisor
rows (`platform_state=New`) enter the main aggregate. Service Health publication
dates come from Azure `impactMitigationTime` (the normalized End time), and
The aggregate includes both Advisor and Service Health rows. The committee
slide projects the combined aggregate and labels each row with its source.

## Service Health Raw Contract

`01_azure_service_health_advisories_raw.tsv` starts with these four columns, in
this exact order:

1. `tracking_id`
2. `short_description_solution`
3. `summary`
4. `description_problem`

The raw schema does not publish the legacy `description` column. The problem
description is plain ASCII: HTML tags are removed, Unicode punctuation is
normalized, and each retained anchor is written as `visible text (URL)`. URLs
remain searchable and are percent-encoded when their path, query, or fragment
contains non-ASCII characters.

`priority` is calculated from a qualified retirement deadline using the existing
priority thresholds. When no qualified deadline exists, the value is `Debito`.
The publication-window date may use broader Service Health time fallbacks, but
`impactStartTime` and `lastUpdateTime` never become a retirement deadline.

Subscription names come from an independent Resource Graph inventory and are
matched case-insensitively. When Azure does not return a name, the row uses the
subscription ID and emits `subscription_name_fallback_to_id` in
`diagnostic_flags`.

Resource resolution uses only Azure-published evidence. The source cascade is:
direct `servicehealthresources` associations, all-state Advisor retirement
associations, and Microsoft-authored `recommendationDataSourceQuery` metadata
queries against the `resources` inventory table. Direct Service Health evidence
has precedence when sources identify the same ARM resource. Resource IDs are
deduplicated case-insensitively by tracking ID, subscription, and ARM ID.

The five resolution columns after `resource_type` are
`resource_resolution_source`, `resource_resolution_status`,
`recommendation_type_id`, `advisor_platform_state`, and `current_query_match`.
Advisor `New` evidence is `active`; existing `Resolved` evidence remains
`resolved`. Deleted resources are excluded from portal-compatible rows but are
counted in the per-tracking diagnostics. When Advisor evidence finds a resource
subscription omitted by the event endpoint, the exporter synthesizes only that
subscription's event row and marks it with
`service_health_subscription_recovered_from_advisor`.

If no evidence-backed resource is available, the event retains its service and
region evidence and uses `not_available` for resource fields and the explicit
resolution placeholders. This is a published-data status, not an inference of
no impact. Coverage remains scope- and permission-dependent; a blank result is
not proof that no resource is affected. Strict live runs stop on source-query
failures or Resource Graph truncation. Degraded runs retain event rows and emit
bounded `query_failed` or `truncated` diagnostics for review.

Legacy fixture and TSV inputs remain readable: an input `description` value is
adapted to `description_problem` at the raw-input boundary and is never emitted
as a canonical output column.

Publication exclusions are reported in run diagnostics as
`publication_advisor_not_current`, `publication_expired`,
`publication_beyond_one_year`, and `publication_missing_or_invalid_date`.

## Workbook Role

The workbook is implementation guidance only. Runtime collection and aggregation do not depend on workbook artifacts.

## Known Limitation

Service Health resource associations are only as complete as the Azure-published
sources visible to the configured scope and identity, including Advisor metadata
permissions and Resource Graph pagination. Rows with unavailable associations
are explicit and must not be interpreted as evidence that Azure found no
impacted resources.

## Validation Workflow

Minimum checks before considering data for executive review:

1. `src/comitato/comitato_azure_retirements/.venv/bin/python -m py_compile src/comitato/comitato_azure_retirements/comitato-azure-retirements.py src/comitato/comitato_azure_retirements/libs/*.py`
2. `src/comitato/comitato_azure_retirements/.venv/bin/python -m pytest -q tests/comitato/comitato_azure_retirements`
3. `bash -n src/comitato/comitato_azure_retirements/run.sh`
4. `shellcheck -s bash src/comitato/comitato_azure_retirements/run.sh`
5. `env PYTHON_BIN=src/comitato/comitato_azure_retirements/.venv/bin/python bash src/comitato/comitato_azure_retirements/run.sh --help`
6. `src/comitato/comitato_azure_retirements/.venv/bin/python src/comitato/comitato_azure_retirements/comitato-azure-retirements.py --help`
