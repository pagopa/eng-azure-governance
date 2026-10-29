# Eng FinOps platform catalog

`eng-finops-platforms.yaml` is the canonical mapping of Eng FinOps platforms
to Azure subscriptions.

The [domain glossary](../../docs/domain/eng-finops-platform-catalog/GLOSSARY.md) defines the catalog vocabulary and its [rules](../../docs/domain/eng-finops-platform-catalog/RULES.md). The repository [architecture](../../docs/architecture.md) records the catalog-to-runtime dependency.

No diagram is provided because this component has one material downstream relationship, already shown in the repository architecture.

## Catalog contract

- The root contains `schema_version: 1` and `platforms`, with an optional
  `tenant_id` UUID. The canonical catalog includes this tenant ID.
- Each platform contains `subscriptions`, which may be empty.
- Each subscription contains `name`, `id`, and `state`.
- `state` must be `active`, `disabled`, or `deleted`.
- Non-null IDs must be valid and unique UUIDs.
- A null ID is allowed only when the subscription is not active.
- Active subscription names must be unique after trimming, lowercasing, and
  collapsing repeated whitespace.

The Azure retirements runtime uses only entries with `state: active` and maps
subscription IDs, as recorded in
[ADR-0003](../../docs/adr/0003-catalog-matching-keys.md). Unsupported or
malformed schemas stop processing with an explicit error. When `tenant_id` is
present, the reader validates it as a UUID; it remains catalog metadata and
does not change subscription matching or runtime scope. Older schema-version-1
catalogs without `tenant_id` remain supported.

## Consumers and validation

The runtime reads and validates the catalog through `src/comitato/comitato_azure_retirements_v2/retirements/adapters/filesystem/platform_catalog_yaml.py`.

Run the focused catalog tests after changing either the schema reader or the catalog:

```bash
src/comitato/comitato_azure_retirements_v2/.venv/bin/python -m pytest -q tests/comitato/comitato_azure_retirements_v2/adapters/test_platform_catalog_yaml.py
```
