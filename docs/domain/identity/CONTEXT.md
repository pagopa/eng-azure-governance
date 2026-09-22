# Identity Context

This context names the repository concepts used to establish its production workload identity and Azure access grants.

## Language

**Production identity**:
The user-assigned identity trusted by the repository's production GitHub environment.
_Avoid_: custom role, policy assignment

**Repository federation**:
The trust relationship that allows the production GitHub environment to request tokens for the production identity.
_Avoid_: client secret, shared credential

**Identity grant**:
An Azure role assignment that gives the production identity one bounded operational capability.
_Avoid_: custom role definition, policy definition

**Identity state**:
The independently managed Terraform state for the repository's identity and its grants.
_Avoid_: policy state, retirement runtime state
