# Azure Retirements v2

This command acquires or reuses saved Azure responses and publishes one validated
monthly report bundle. The default selector is `all`; use `--report`
with `advisor`, `service-health`, `aggregate`, or `slides` to publish one
selected contract and its complete dependency closure.

## Contents

- [Package Layout](#package-layout)
- [Advisor Enrichment](#advisor-enrichment)
- [Download Reuse And Timeouts](#download-reuse-and-timeouts)
- [Published Artifacts](#published-artifacts)
- [Operator Output And Logging](#operator-output-and-logging)
- [Service Health Evidence](#service-health-evidence)

## Package Layout

Run `bash src/comitato/comitato_azure_retirements_v2/run.sh --help` to inspect
the CLI before a live run. The component root keeps `data/` and `exports/`
beside the canonical `retirements/` package; its sole Python entry script is
`comitato-azure-retirements-v2.py`.

Use the canonical import namespace
`src.comitato.comitato_azure_retirements_v2.retirements`; do not import a
top-level `retirements` package. Default output paths are unchanged: component
`exports/YYYY/MM`, component `data/comitato_editoriale.yaml`, and repository
`tmp/comitato/comitato_azure_retirements_v2/exports` for debug logs.

Required access is read access to the selected subscription scope for Azure
Advisor, Resource Health events, Resource Graph enrichment, and subscription
scope resolution. Authentication uses `AZURE_BEARER_TOKEN` when supplied or
the logged-in Azure CLI account. Tokens are never written to configuration,
diagnostics, manifests, or artifacts.

## Advisor Enrichment

Advisor raw recommendations are enriched from three Azure sources: the
`Microsoft.Advisor/metadata` endpoint, Resource Graph resource inventory, and
Resource Graph subscription inventory. Resource inventory is queried by
normalized ARM resource ID, while subscription names come only from the
`resourcecontainers` subscription inventory. Each raw TSV row keeps one
companion JSONL record containing the recommendation and the matched enrichment
evidence.

Missing optional values are not synthesized. `service_name` may use a
deterministic resource-type fallback, but `subscription_name`,
`learn_more_link`, `label`, and `potential_benefits` are never invented. Empty
authoritative values remain empty and are recorded in row diagnostics and field
provenance. Transport, pagination, response-shape, repeated-continuation, and
ambiguous-join failures block publication; a failed enrichment acquisition
leaves the existing monthly bundle unchanged.

The operator supplies `--subscriptions sub-a,sub-b` or allows live scope
resolution. `--catalog-path` selects the source-of-truth version-1 platform
catalog; `--output-path` selects the export root. Relative defaults are
resolved from the repository root: the catalog is
`src/_source_of_truth/eng-finops-platforms.yaml`, and the export root is
`src/comitato/comitato_azure_retirements_v2/exports`. The catalog and output
root may be set with `COMITATO_AZURE_RETIREMENTS_CATALOG` and
`COMITATO_AZURE_RETIREMENTS_OUTPUT`. `--committee-yaml` selects the committee
sidecar path; the composition default is
`src/comitato/comitato_azure_retirements_v2/data/comitato_editoriale.yaml`.

Each successful run writes its complete bundle under
`exports/YYYY/MM`, where the partition comes from `--as-of-date`. A later run
for the same month replaces that entire monthly directory, including files
left by an earlier selector or run. Runs for other months keep their existing
bundles.

Replacing an existing month deletes the superseded bundle after the new bundle
becomes current. Save a copy elsewhere before replacing a bundle that may need
to be replayed later. New publication and replay use the hashed `saved_inputs`
in `publication-manifest.json`. A live slide run merges committee values from
`comitato_editoriale.yaml` into the slide before encoding and writes the YAML
only after publication succeeds. A changed original description clears
`comitato_descrizione` and its editorial references in `comitato_fonti`;
`comitato_retirement_date` is retained, and entries not present in the run are
dropped. Unchanged source descriptions retain both editorial fields. New and
legacy entries without editorial references default to `comitato_fonti: []`.
Pass `--committee-yaml PATH` to select another file.
In the YAML, `comitato_descrizione` contains only a plain-text, service-first
description and a plain `Suggerimento:` paragraph, without Markdown formatting
or source links. `comitato_fonti` holds editorial references as a list of
`{titolo: str, url: str}` mappings, separate from the original `link_fonti`.
Editorial references stay in the YAML; they do not add a TSV column.
Descriptions longer than 100 characters use folded style,
`link_fonti` omits Azure portal links (`app.azure.com`, `portal.azure.com`,
`aka.ms/AzureServiceHealthAdvisories`), and `retirement_date` is a list of
`{data, tipo, fonte}` entries. Schema-1 historical bundles without `saved_inputs` cannot be replayed
because they do not preserve the acquisition inputs needed for deterministic
replay.

### Refresh Committee Values Locally

Use the [local-azure-retirements-enrich skill](../../../.github/skills/local-azure-retirements-enrich/SKILL.md)
to complete missing editorial fields for a selected year and month. The skill
saves the YAML and presents a change summary first. It runs the launcher only
after explicit user approval of that summary.

Use the existing monthly bundle as replay input to apply editorial YAML without
acquiring Azure data:

```bash
bash src/comitato/comitato_azure_retirements_v2/run.sh \
  --replay-bundle src/comitato/comitato_azure_retirements_v2/exports/2026/10 \
  --refresh-committee \
  --committee-yaml src/comitato/comitato_azure_retirements_v2/data/comitato_editoriale.yaml \
  --output-path src/comitato/comitato_azure_retirements_v2/exports \
  --output-format json
```

The manifest supplies the original report selector, date, subscription scope,
and saved inputs. All reports selected by that manifest are republished; only
the slide's committee fields are enriched. The editorial YAML is read but not
rewritten, so entries for other months remain intact. The bundle must contain
saved inputs and publish slides, and the YAML must exist. Ordinary replay
continues to ignore editorial YAML unless `--refresh-committee` is explicit.
The existing original-description match rule still applies: stale descriptions
are not reused. Run from the repository root and use explicit paths to avoid
environment-variable output overrides.

## Download Reuse And Timeouts

The Advisor and Service Health pipelines run concurrently with at most two
workers, including each source's enrichment downloads. Each worker uses its own
HTTP session. Each source first acquires its main data (stage 1/2), then its
enrichment evidence (stage 2/2). Subscription traversal and pagination within
each source remain ordered. Aggregation and publication wait for both pipelines
to finish successfully.

Download logs identify the owning source, operation, stage, subscription ID,
current subscription/total, and page. They distinguish a live request from a
download saved to cache and a cache hit. Completion messages include the record
count, elapsed time, original download timestamp, and whether more pages remain.
For example:

```text
[Service Health | events | 1/2 main acquisition | subscription sub-example | 2/10 subscriptions | page 1] Downloaded and cached; 12 records; last page; remaining subscriptions 8; estimated remaining 24.0s (main acquisition only); elapsed 3.0s; downloaded at ...
[Advisor | Resource Graph resource inventory | 2/2 enrichment | batch 1/3 | page 1] Reused cache; 50 records; last page of batch; remaining batches 2; elapsed 0.0s; downloaded at ...
```

The remaining-time estimate uses the observed mean time per completed
subscription and covers only that source's main acquisition. Cache hits, varying
subscription sizes, retries, and throttling can change the estimate. Before a
subscription finishes, no ETA is asserted. Azure does not announce a total page
count: logs say `more pages pending (total unknown)` until the last page rather
than inventing a page percentage or a report-wide ETA. Each completed pipeline
reports the finished/total and remaining source counts. Retries identify their
source and page, next attempt/maximum attempts, and backoff delay.
Resource inventory lookups show `batch X/Y` for groups of up to 100 unique
resource IDs. Page numbering restarts within each batch. `last page of batch`
and the remaining batch count distinguish the end of one query from the end of
the whole lookup, including when responses come from cache.

Successful Azure response objects are saved atomically under
`<output-path>/.acquisition-cache/` (by default
`src/comitato/comitato_azure_retirements_v2/exports/.acquisition-cache/`).
The cache includes Advisor recommendations, Service Health events, Advisor
metadata, and Resource Graph enrichment responses. It is independent of monthly
publication and survives failed runs and replacement of a monthly bundle.
Subscription scope resolution remains live unless subscriptions are explicit.

Cache entries have **no expiry**, including across report months. A later run
reuses existing entries and downloads only missing requests. Request identity
includes the method, full URL, API version, query parameters, and POST body,
so different subscriptions, queries, and continuation pages remain distinct.
The cache is per response, not per report: completed pages survive a timeout on
a later page. An incomplete acquisition still blocks publication.

This is a saved snapshot, not an automatic refresh. New Azure notices and
updates are invisible until the relevant cache entries are removed. A cache-hit
event shows the original download timestamp on the human console and in the
debug log. To refresh, stop active runs and delete
`<output-path>/.acquisition-cache/`, or delete individual JSON entries to
download only those requests again. Changing `--as-of-date` alone does not
refresh Azure data. A resumed run can combine older completed responses with
newly downloaded ones; clear the cache for a wholly fresh acquisition.

Cache files contain Azure response data and must be treated like raw exports.
They are excluded from Git, use private temporary files, and never store
authentication headers or bearer tokens. Checksums detect damaged payloads.
A corrupt or unreadable entry fails explicitly rather than silently triggering
a new download; remove the indicated entry to recover. Disk-write failures also
fail explicitly and do not leave a partial cache entry.

`--timeout-seconds` controls the timeout for each HTTP attempt (default: 60).
`--retry-attempts` controls additional attempts (default: 3). Read and connection
timeouts now use the same bounded retry/backoff policy as retryable HTTP
responses (408, 429, 500, 502, 503, 504). The default allows at most four attempts;
a persistently slow endpoint can therefore still fail after exhausting its
budget. Use a larger timeout, for example `./run.sh --timeout-seconds 120`, when
the endpoint consistently needs more than 60 seconds. A failed run leaves the
previous monthly bundle unchanged and keeps completed cached responses.

## Published Artifacts

The `all` artifact set contains both raw TSV/JSONL evidence pairs, the
aggregate TSV, the slide-preparation TSV, and `publication-manifest.json`.
Single selectors publish only their selected set; upstream dependencies remain
run-local. A private same-filesystem bundle is staged, reread, hashed, and
validated before it replaces the target month. Failed runs return a non-zero
status and emit sorted JSONL diagnostics on stderr without changing the
existing monthly bundle.

The complete aggregate retains source membership independently of the
committee view. The slide artifact has exactly these 19 columns, in order:
`id_elemento`, `titolo_breve`, `descrizione_breve`, `comitato_priorità`,
`impatto_microsoft`, `comitato_descrizione`, `comitato_retirement_date`,
`comitato_piattaforme`, `retirement_date`, `stato_data`, `giorni_ritardo`,
`descrizione_originale_completa`, `azione_originale`, `fonti`, `link_fonti`,
`ambito_impatto`, `id_advisor`, `id_service_health`, `risorse_json`.
Rows group by Advisor recommendation type id, then Service Health tracking id,
then aggregate id. Stable slide ids use the `azure-retirement:v2:` prefix.
`descrizione_breve` uses the first problem title, with retiring feature and
service as fallbacks. `impatto_microsoft` maps the highest Advisor impact to
`Alto`, `Medio`, or `Basso`; Service Health-only rows leave it empty.
`retirement_date` lists every date with its meaning: Advisor recommendation
and metadata retirement dates, image removal dates, Service Health notice
window, and the oldest and latest observed update per source. Only retirement
dates, or the nearest image removal date when none exists, drive `stato_data`
and ordering; differing recommendation and metadata dates yield `Date
discordanti`. `giorni_ritardo` holds the days since the deadline for `Scaduta`
rows only. `id_advisor` and `id_service_health` are portal links to the
recommendation type and the Service Health tracking id. Rows beyond the
committee window are excluded; the remaining date states are `Data non
disponibile`, `Date discordanti`, `Scaduta`, and `In scadenza`.

Replay does not read or write `comitato_editoriale.yaml`, so replayed slide
committee cells are empty. The live YAML is independent from the published
monthly bundle. Priority remains an external decision. `ambito_impatto` records
platform, subscription, resource, environment, service, and region counts;
`risorse_json` is compact and groups resource names by platform, subscription,
and resource group. Cells longer than the Excel limit of 32,767 characters are
not truncated by this projection contract.

## Operator Output And Logging

The launcher and direct script entry point have different defaults:

- `run.sh` appends `--output-format human` when no output format was supplied.
  It shows the human layout and bootstrap status lines only when stderr is an
  interactive TTY.
- Direct execution of `comitato-azure-retirements-v2.py` defaults to machine
  output. Successful runs write one JSON value and a newline to stdout.
  Failures write sorted JSONL diagnostics to stderr.
- `--output-format json` always uses the machine contract, even in a TTY.
- `--output-format human` uses Rich on stderr only in a TTY. In non-TTY
  execution it falls back to the machine JSON or JSONL contract.
- Launcher bootstrap status lines are suppressed in non-TTY execution and
  whenever an explicit JSON format is supplied. Human output never shares
  stdout with machine payloads.

Every enabled run writes a UTF-8 plain-text debug log. The default path is:

```text
tmp/comitato/comitato_azure_retirements_v2/exports/YYYY/MM/<YYYYMMDDHHMM>_<run-id>_debug.log
```

The month partition is based on the run start time. `--log-directory` changes
the debug-log root while preserving the same `YYYY/MM` partition and filename
pattern. This path is separate from `--output-path`: changing logging settings
does not redirect, replace, or otherwise alter the published artifact bundle.

Use the logging flags as follows:

- `--output-format {human,json}` selects the process output contract.
- `--verbose` includes additional non-failing runtime events in the human
  console and debug log.
- `--log-level LEVEL` sets the minimum level written to the debug log.
- `--console-level LEVEL` sets the minimum level rendered in human mode.
  Accepted levels are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`.
- `--no-debug-log` disables the durable text log and creates no log directory.
- `--log-directory PATH` selects a separate debug-log root without creating it
  during argument parsing.

Debug events contain bounded lifecycle metadata such as stage names, source
names, counts, logical paths, status codes, and run or subscription identifiers.
They never contain bearer tokens, authorization or request headers, URL query
strings, complete request payloads, or response bodies. Debug logging is
independent of publication success and does not change artifact bytes.

Examples:

```bash
bash src/comitato/comitato_azure_retirements_v2/run.sh --help
bash src/comitato/comitato_azure_retirements_v2/run.sh \
  --report all \
  --subscriptions 00000000-0000-0000-0000-000000000000 \
  --as-of-date 2026-07-31 \
  --catalog-path src/_source_of_truth/eng-finops-platforms.yaml \
  --output-path src/comitato/comitato_azure_retirements_v2/exports
```

For an interactive operator run, omit `--output-format` and keep stderr
attached to the terminal:

```bash
bash src/comitato/comitato_azure_retirements_v2/run.sh \
  --report all \
  --subscriptions 00000000-0000-0000-0000-000000000000 \
  --as-of-date 2026-07-31
```

For automation, select JSON explicitly and parse stdout while keeping stderr
available for JSONL diagnostics:

```bash
python3 \
  src/comitato/comitato_azure_retirements_v2/comitato-azure-retirements-v2.py \
  --output-format json \
  --report aggregate \
  --subscriptions 00000000-0000-0000-0000-000000000000 \
  > result.json
python3 -c 'import json, pathlib; print(json.loads(pathlib.Path("result.json").read_text())["status"])'
```

## Service Health Evidence

Service Health advisories are acquired from the Resource Health events endpoint
at `subscriptions/{subscriptionId}/providers/Microsoft.ResourceHealth/events`
with API version `2025-05-01`. The raw event and its original text remain in
the JSONL companion. The TSV projection parses `properties.impact`, preserves
Unicode, and renders readable HTML-derived title, summary, description, and
recommended-action fields.

Presentation material and external investigations are reconciliation evidence,
not acquisition sources. They do not add API records, prove complete Azure
coverage, or justify a target row count. Reconciliation must account for Azure
scope, filtering, paging, access, collection evidence, and human inspection of
the final TSV and committee YAML.

The supplemental Resource Graph adapter uses the scoped,
paginated `Microsoft.ResourceGraph/resources?api-version=2024-04-01` endpoint
for three purposes:

1. Resolve subscription names from the live `resourcecontainers` inventory,
  with the governed platform catalog as fallback.
2. Acquire impacted-resource associations from `servicehealthresources` for
  `microsoft.resourcehealth/events/impactedresources`.
3. Query verified metadata in `resources` only for target resource IDs already
  published by those Service Health associations.

A completed impacted-resource query with no matching target is represented as
`resource_evidence_status=not_published`; it does not infer an ARM resource
from article text, service, region, or subscription data. Resource Graph
transport, pagination, or response-shape failures block the run and leave the
existing monthly bundle unchanged. Query labels and subscription-name source
are retained in `provenance_json`.
