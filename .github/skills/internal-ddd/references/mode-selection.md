# DDD Mode Selection

Choose the smallest DDD mode that relieves the current domain pressure.

| Pressure | Prefer | Why | Anti-trigger |
| --- | --- | --- | --- |
| Teams disagree on terms, ownership, or boundaries | Strategic | The main risk is model collision, not class design | Do not jump to aggregates before the contexts are named |
| A single bounded context has unstable invariants or confusing entity responsibilities | Tactical | The boundary exists, but the inside model is weak | Do not add evented patterns just to compensate for poor tactical modeling |
| Workflows cross contexts asynchronously and require auditability, replay, or compensations | Evented | The integration and lifecycle pressure justify operational complexity | Do not recommend event sourcing, CQRS, or sagas without explicit operational need |
| Rules are stable, ownership is obvious, and the problem is straightforward CRUD | No DDD escalation | Extra DDD ceremony would add drag without protecting real complexity | Use simpler architecture and record why DDD was rejected |

## Escalation rule

Prefer this order unless existing system pressure proves otherwise:

1. Strategic
2. Tactical
3. Evented

Escalate only when the lower mode no longer explains the current risk.
