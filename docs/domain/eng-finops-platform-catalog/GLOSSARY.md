# Eng FinOps Platform Catalog

This context names the repository concepts used to map Azure subscriptions to Eng FinOps platforms.

## Language

**Eng FinOps platform**:
A named organizational grouping for Azure subscriptions in the canonical catalog.
_Avoid_: Azure service, retirement source

**Catalog subscription**:
A subscription entry associated with one Eng FinOps platform and one lifecycle state.
_Avoid_: runtime scope, policy assignment

**Subscription state**:
The catalog lifecycle marker `active`, `disabled`, or `deleted` attached to a subscription entry.
_Avoid_: Azure resource state, runtime status

**Active platform mapping**:
The subscription-to-platform relationship made available to catalog consumers for active entries only.
_Avoid_: inferred platform

**Catalog schema version**:
The integer contract that identifies the supported shape of the canonical catalog.
_Avoid_: application version, Terraform version

**Catalog tenant ID**:
The Azure tenant UUID recorded as catalog metadata; it does not determine subscription mappings.
_Avoid_: subscription ID, runtime scope
