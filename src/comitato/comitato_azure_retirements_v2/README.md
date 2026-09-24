# Azure Retirements v2

This command performs a live Azure acquisition and publishes one validated
monthly report bundle. The default selector is `all`; use `--report`
with `advisor`, `service-health`, `aggregate`, or `slides` to publish one
selected contract and its complete dependency closure.

Required access is read access to the selected subscription scope for Azure
Advisor, Resource Health events, Resource Graph enrichment, and subscription
scope resolution. Authentication uses `AZURE_BEARER_TOKEN` when supplied or
the logged-in Azure CLI account. Tokens are never written to configuration,
diagnostics, manifests, or artifacts.

## Advisor Enrichment

Advisor raw recommendations are enriched from three live sources: the
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
only after publication succeeds. A changed original description clears only
`comitato_descrizione`; `comitato_retirement_date` is retained, and entries not
present in the run are dropped. Pass `--committee-yaml PATH` to select another
file. In the YAML, descriptions longer than 100 characters use folded style,
`link_fonti` omits Azure portal links (`app.azure.com`, `portal.azure.com`,
`aka.ms/AzureServiceHealthAdvisories`), and `retirement_date` is a list of
`{data, tipo, fonte}` entries. Schema-1 historical bundles without `saved_inputs` cannot be replayed
because they do not preserve the acquisition inputs needed for deterministic
replay.

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

The launcher and direct module entry point have different defaults:

- `run.sh` appends `--output-format human` when no output format was supplied.
  It shows the human layout and bootstrap status lines only when stderr is an
  interactive TTY.
- Direct `python -m src.comitato.comitato_azure_retirements_v2` execution
  defaults to machine output. Successful runs write one JSON value and a
  newline to stdout. Failures write sorted JSONL diagnostics to stderr.
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

## Service Health Evidence

Service Health advisories are acquired from the Resource Health events endpoint
at `subscriptions/{subscriptionId}/providers/Microsoft.ResourceHealth/events`
with API version `2025-05-01`. The raw event and its original text remain in
The JSONL companion. The TSV projection parses `properties.impact`, preserves
Unicode, and renders readable HTML-derived title, summary, description, and
recommended-action fields.

The supplied PDF and any `9PN5-64G` investigation are reconciliation or
evidence obligations only. They do not add API records, prove complete Azure
coverage, or justify a target row count. MO-01 must record the authoritative
Azure scope, filtering, paging, access, and collection evidence for `9PN5-64G`.
MO-02 must classify every July presentation reference without treating its row
count as a target. MO-03 is the human inspection of the final 19-column TSV
and adjacent YAML, including Unicode, multiline text, actions, resources,
editorial ownership, drafts, and sidecar retention.

The supplemental Resource Graph adapter uses the scoped,
paginated `Microsoft.ResourceGraph/resources?api-version=2024-04-01` endpoint
for three purposes:

1. Subscription names, with live inventory preferred over the governed platform
  catalog fallback:

  ```kusto
  resourcecontainers
  | where type =~ "microsoft.resources/subscriptions"
  | project subscriptionId, subscriptionName=name
  ```

1. Service Health impacted-resource associations:

  ```kusto
  servicehealthresources
  | where type =~ "microsoft.resourcehealth/events/impactedresources"
  | project id, subscriptionId, properties
  ```

1. Verified metadata for target resource IDs already published by the Service
  Health association query:

  ```kusto
  resources
  | where tolower(id) in ("/subscriptions/.../providers/...")
  | project id, name, type, location, resourceGroup, subscriptionId, tags, resourceId = tolower(id)
  ```

A completed impacted-resource query with no matching target is represented as
`resource_evidence_status=not_published`; it does not infer an ARM resource
from article text, service, region, or subscription data. Resource Graph
transport, pagination, or response-shape failures block the run and leave the
existing monthly bundle unchanged. Query labels and subscription-name source
are retained in `provenance_json`.

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
  --catalog-path config/eng-finops-platforms.yaml \
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
python3 -m src.comitato.comitato_azure_retirements_v2 \
  --output-format json \
  --report aggregate \
  --subscriptions 00000000-0000-0000-0000-000000000000 \
  > result.json
python3 -c 'import json, pathlib; print(json.loads(pathlib.Path("result.json").read_text())["status"])'
```
