# Azure Retirements v2

This command performs a live Azure acquisition and publishes one atomic,
validated report generation. The default selector is `all`; use `--report`
with `advisor`, `service-health`, `aggregate`, or `slides` to publish one
selected contract and its complete dependency closure.

Required access is read access to the selected subscription scope for Azure
Advisor, Resource Health events, Resource Graph enrichment, and subscription
scope resolution. Authentication uses `AZURE_BEARER_TOKEN` when supplied or
the logged-in Azure CLI account. Tokens are never written to configuration,
diagnostics, manifests, or artifacts.

The operator supplies `--subscriptions sub-a,sub-b` or allows live scope
resolution. `--catalog-path` selects the source-of-truth version-1 platform
catalog; `--output-path` selects the publication directory. The catalog and
output paths default to `eng-finops-platforms.yaml` and `output` and may be
set with `COMITATO_AZURE_RETIREMENTS_CATALOG` and
`COMITATO_AZURE_RETIREMENTS_OUTPUT`.

The `all` artifact set contains both raw TSV/JSONL evidence pairs, the
aggregate TSV, the slide-preparation TSV, and `publication-manifest.json`.
Single selectors publish only their selected set; upstream dependencies remain
run-local. A private same-filesystem generation is staged, reread, hashed, and
validated before one atomic `current` reference switch. Failed runs return a
non-zero status and emit sorted JSONL diagnostics on stderr without changing
the current generation.

Examples:

```bash
bash src/comitato/comitato_azure_retirements_v2/run.sh --help
bash src/comitato/comitato_azure_retirements_v2/run.sh \
  --report all \
  --subscriptions 00000000-0000-0000-0000-000000000000 \
  --as-of-date 2026-07-31 \
  --catalog-path config/eng-finops-platforms.yaml \
  --output-path exports/azure-retirements
```
