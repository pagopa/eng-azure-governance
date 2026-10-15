# ADR-0003: Match catalog entries by runtime-specific keys

* Status: accepted
* Date: 2026-10-14
* Deciders: Repository owner
* Related: [Eng FinOps Platform Catalog rules](../domain/eng-finops-platform-catalog/RULES.md), [architecture](../architecture.md)

## Context and Problem Statement

The architecture stated that catalog subscription IDs must not be used as runtime matching keys. The retirement runtime maps catalog entries by subscription ID, and the repository needs one recorded rule for it.

## Domain Evidence

| Evidence | Finding |
| --- | --- |
| `src/comitato/comitato_azure_retirements_v2/retirements/adapters/filesystem/platform_catalog_yaml.py` | The v2 reader validates subscription UUIDs and keys assignments by subscription ID. |
| `src/comitato/comitato_azure_retirements_v2/retirements/application/orchestration.py` | v2 coverage compares acquired subscriptions with the catalog subscription IDs. |
| `src/_source_of_truth/eng-finops-platforms.yaml` | Every active entry carries both a name and a UUID. |

## Decision Drivers

* Use a stable key that survives subscription renames.
* Remove the contradiction between the architecture and the v2 implementation.

## Considered Options

* Match by normalized subscription name.
* Match by subscription ID.

## Decision Outcome

Chosen option: "Match by subscription ID", because the subscription ID is the stable key.

The architecture restriction on subscription IDs as matching keys is removed; the retirement runtime matches by subscription ID. The catalog schema is unchanged.
