# DDD Deliverables

Use this checklist to keep DDD adoption practical and stage-specific.

## Strategic deliverables

- Subdomain map with core, supporting, and generic domains
- Bounded context map with ownership and key upstream or downstream relationships
- Ubiquitous language glossary for the current problem slice
- Cross-context translation seams or anti-corruption boundaries where the language changes
- One or two ADRs documenting the critical boundary decisions

Exit criteria:

- Team boundaries and model ownership are explicit
- Major translation seams are named
- The next tactical or integration work can proceed without redefining terms

## Tactical deliverables

- Aggregate list with explicit invariants
- Value object list and the rules they protect
- Domain service list only where behavior does not belong inside an aggregate
- Repository contracts and transaction boundaries

Exit criteria:

- Invariants have one clear enforcement home
- Entity and value-object boundaries are explainable in domain language
- Persistence and transaction seams follow the model instead of leaking into it

## Evented deliverables

- Command and query separation rationale
- Domain-event list with ownership and publication boundaries
- Read-model or projection ownership plus freshness expectations
- Event-history-as-source-of-truth rationale when event sourcing is proposed
- Event schema versioning policy
- Projection rebuild or replay strategy
- Saga or process-manager compensation matrix when long-running workflow coordination exists

Exit criteria:

- There is a clear reason to pay the operational cost of evented patterns
- CQRS, event sourcing, or read-model complexity is justified instead of assumed
- Rebuild, replay, and failure handling are defined before implementation starts
- Consumers and ownership of each event stream are explicit
