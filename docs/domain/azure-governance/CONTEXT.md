# Azure Governance Context

This context names the repository concepts used to define, group, assign, and remediate Azure governance controls.

## Language

**Custom role**:
A repository-defined Azure RBAC role whose permissions are limited to a governance responsibility.
_Avoid_: broad built-in role, authorization assignment

**Policy definition**:
An individual Azure Policy control describing the condition and effect applied to governed resources.
_Avoid_: policy assignment, initiative

**Policy family**:
A set of related policy definitions maintained for one Azure service or governance concern.
_Avoid_: policy set

**Policy set**:
An Azure Policy initiative that groups policy definitions for a shared governance purpose.
_Avoid_: policy family, assignment

**Policy assignment**:
The binding of a policy definition or policy set to a management group or subscription scope.
_Avoid_: policy definition, custom role

**Remediation**:
An Azure operation that acts on resources reported as non-compliant by an assigned policy.
_Avoid_: drift detection, policy evaluation

**Apply order**:
The repository sequence in which custom roles, policy definitions, policy sets, and assignments are applied: `01` through `04`.
_Avoid_: deployment order, runtime order
