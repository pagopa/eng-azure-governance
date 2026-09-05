# Eng FinOps platform catalog

`eng-finops-platforms.yaml` is the canonical mapping of Eng FinOps platforms
to Azure subscriptions.

The [domain context](../../docs/domain/eng-finops-platform-catalog/CONTEXT.md) defines the catalog vocabulary and its [rules](../../docs/domain/eng-finops-platform-catalog/RULES.md). The repository [architecture](../../docs/architecture.md) records the catalog-to-runtime dependency.

No diagram is provided because this component has one material downstream relationship, already shown in the repository architecture.

## Catalog contract

- The root contains only `schema_version: 1` and `platforms`.
- Each platform contains `subscriptions`, which may be empty.
- Each subscription contains `name`, `id`, and `state`.
- `state` must be `active`, `disabled`, or `deleted`.
- Non-null IDs must be valid and unique UUIDs.
- A null ID is allowed only when the subscription is not active.
- Active subscription names must be unique after trimming, lowercasing, and
  collapsing repeated whitespace.

The Azure retirements runtime maps subscription names to platforms using only
entries with `state: active`. Subscription IDs are validated metadata and are
not matching keys. Unsupported or malformed schemas stop processing with an
explicit error.

## Consumers and validation

`src/comitato/comitato_azure_retirements/libs/runtime_runner.py` resolves the canonical catalog path, and `platform_catalog.py` validates it before aggregate generation. No other checked-in consumer is evidenced.

Run the focused catalog tests after changing either the schema reader or the catalog:

```bash
src/comitato/comitato_azure_retirements/.venv/bin/python -m pytest -q tests/comitato/comitato_azure_retirements/test_platform_catalog.py
```
