# ADR-0003: Match catalog entries by runtime-specific keys

* Status: accepted
* Date: 2026-10-14
* Deciders: Repository owner
* Related: [Eng FinOps Platform Catalog rules](../domain/eng-finops-platform-catalog/RULES.md), [architecture](../architecture.md)

## Context and Problem Statement

The architecture stated that catalog subscription IDs must not be used as runtime matching keys. The v1 retirement runtime maps active entries by normalized subscription name, but the v2 runtime maps catalog entries by subscription ID. The repository needs one recorded rule for how each runtime matches catalog entries.

## Domain Evidence

| Evidence | Finding |
| --- | --- |
| `src/comitato/comitato_azure_retirements/libs/platform_catalog.py` | The v1 reader exposes active mappings keyed by normalized subscription name. |
| `src/comitato/comitato_azure_retirements_v2/retirements/adapters/filesystem/platform_catalog_yaml.py` | The v2 reader validates subscription UUIDs and keys assignments by subscription ID. |
| `src/comitato/comitato_azure_retirements_v2/retirements/application/orchestration.py` | v2 coverage compares acquired subscriptions with the catalog subscription IDs. |
| `src/_source_of_truth/eng-finops-platforms.yaml` | Every active entry carries both a name and a UUID. |

## Decision Drivers

* Use a stable key that survives subscription renames.
* Keep the v1 runtime valid while it remains in use.
* Remove the contradiction between the architecture and the v2 implementation.

## Considered Options

* Match by normalized subscription name in both runtimes.
* Match by subscription ID in v2 and keep normalized-name matching in v1.

## Decision Outcome

Chosen option: "Match by subscription ID in v2 and keep normalized-name matching in v1", because the subscription ID is the stable key and v1 keeps its existing contract.

The architecture restriction on subscription IDs as matching keys now applies to the v1 runtime only. The catalog schema is unchanged.
