# Azure Operations Validation And Evidence

Use this reference when the base skill needs a deeper operational checklist.

## Preflight checklist

- confirm scope and rollout unit
- confirm rollback trigger and owner
- confirm monitoring, alerting, and logging signals for the affected surface
- confirm backup or recovery expectations when stateful services are involved
- confirm identity and policy assumptions before widening rollout

## Rollout validation

- validate the first safe unit before widening scope
- check both success signals and unexpected deny, drift, or connectivity regressions
- record what was actually observed versus what was only expected

## Post-rollout evidence

- audit trail for what changed
- evidence that preventive controls still allow intended operations
- evidence that Azure Monitor and Log Analytics still receive the expected signals
- evidence that restore or recovery assumptions were tested when relevant

## BC/DR note

BC/DR stays optional here as well.

Load it when the rollout affects continuity expectations, recovery posture, or business-critical platform capability.

## Azure Monitor and Log Analytics evidence patterns

| Surface | Signals to check | What they confirm |
| --- | --- | --- |
| Identity or RBAC rollout | Sign-in or activity signals, denied action evidence, successful intended operations | The access model still permits intended work and surfaces regressions |
| Policy rollout | Compliance state, remediation outcome, and exceptions still scoped correctly | Guardrails applied as expected without unintended drift |
| Platform topology or shared services | Health, logs, and alert continuity for the affected control plane | The rollout did not break core visibility or routing |

## Backup versus restore proof expectations

| Need | Acceptable proof | Not enough on its own |
| --- | --- | --- |
| Backup posture exists | Protected resource inventory, backup policy attachment, recent job success | A claim that backup is enabled |
| Restore is viable | Restore exercise, observed recovery time, integrity check after recovery | Backup success without a restore test |
| DR posture is credible | Site Recovery or equivalent continuity exercise for the scoped service | General health signals during normal operations |

## Stage-aware rollout evidence

| Rollout stage | Evidence to collect before widening |
| --- | --- |
| First management group or subscription set | Inheritance behaves as expected, monitoring is still present, rollback owner confirmed |
| First landing-zone or platform slice | Connectivity, automation, and alerting still work under the new design |
| Broad subscription or region expansion | Prior wave observations recorded, regressions investigated, escalation path confirmed |
