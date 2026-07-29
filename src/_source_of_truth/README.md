# Eng FinOps platform catalog

`eng-finops-platforms.yaml` is the canonical mapping of Eng FinOps platforms
to Azure subscriptions.

## Schema version 1

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
