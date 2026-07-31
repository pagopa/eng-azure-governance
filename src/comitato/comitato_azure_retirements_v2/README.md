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

The operator supplies `--subscriptions sub-a,sub-b` or allows live scope
resolution. `--catalog-path` selects the source-of-truth version-1 platform
catalog; `--output-path` selects the export root. Relative defaults are
resolved from the repository root: the catalog is
`src/_source_of_truth/eng-finops-platforms.yaml` and the export root is
`src/comitato/comitato_azure_retirements_v2/exports`. Both may be set with
`COMITATO_AZURE_RETIREMENTS_CATALOG` and `COMITATO_AZURE_RETIREMENTS_OUTPUT`.

Each successful run writes its complete bundle under
`exports/YYYY/MM`, where the partition comes from `--as-of-date`. A later run
for the same month replaces that entire monthly directory, including files
left by an earlier selector or run. Runs for other months keep their existing
bundles.

The `all` artifact set contains both raw TSV/JSONL evidence pairs, the
aggregate TSV, the slide-preparation TSV, and `publication-manifest.json`.
Single selectors publish only their selected set; upstream dependencies remain
run-local. A private same-filesystem bundle is staged, reread, hashed, and
validated before it replaces the target month. Failed runs return a non-zero
status and emit sorted JSONL diagnostics on stderr without changing the
existing monthly bundle.

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
