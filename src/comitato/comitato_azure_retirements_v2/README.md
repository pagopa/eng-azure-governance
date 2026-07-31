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
