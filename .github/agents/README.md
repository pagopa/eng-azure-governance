# Agents Catalog

This checkout has no repository-local `*.agent.md` files. This directory is
reserved for optional custom agents; it does not install editor or user-level
agents.

## Resolution order

1. Apply the current request within the repository's safety and authority boundaries.
2. Apply [AGENTS.md](../../AGENTS.md) and its [local policy](../../AGENTS.local.md).
3. Apply matching [path-specific review instructions](../INVENTORY.md#instructions).
4. Apply the selected prompt or available skill within its declared scope.

## Task routing

- Use the [documentation index](../../docs/README.md) to resolve domain owners.

The editor's active agent executes authorized changes. A prompt name is not
an installed agent, and a user-installed skill is not a file in this directory.

## Validation

If custom agents are added, register their exact paths in the
[inventory](../INVENTORY.md#agents) and run the native inventory check described
in the [configuration guide](../README.md#validation).

No diagram is provided because this README is a flat routing catalog; the
resolution order and task links above describe its relationships more
precisely than a separate diagram.
