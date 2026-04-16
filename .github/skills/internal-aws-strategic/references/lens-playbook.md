# AWS Strategic Lens Playbook

Use this reference when the user wants more depth than the base skill should load by default.

## Common lens combinations

| Situation | Start with | Add only if needed |
| --- | --- | --- |
| High-level landing-zone or control-plane choice | organization-structure, governance | FinOps, BC/DR |
| Identity or delegated access choice | identity and access, governance | blast radius, compliance |
| Rollout planning across accounts or OUs | rollout and rollback, blast radius | operations, BC/DR |
| Cost-sensitive platform decision | FinOps, maintainability | operations, governance |
| Resilience-sensitive design | BC/DR, operations | FinOps, blast radius |

## Signals that another lens should be suggested

- Cost could materially change the recommended option: suggest `FinOps`
- A failure would interrupt critical platform capability: suggest `BC/DR`
- The choice changes account, OU, or network topology: suggest `organization-structure`
- The choice changes permissions, trust, or preventive controls: suggest `governance`
- The choice adds operational burden or verification work: suggest `operations`

## Depth control

- Stay in `Quick answer` mode when one option is clearly better and the user asked a narrow question.
- Upgrade to `Decision note` when at least two viable options exist.
- Upgrade to `Deep analysis` only when the user asks for it or the risk profile justifies it.

## Worked AWS decision shapes

### Landing-zone or control-plane choice

| Situation | Frame first | Recommendation shape |
| --- | --- | --- |
| New multi-account platform with centralized controls | `organization-structure`, `governance` | Compare a thin management account plus delegated administrators against a more centralized operating model, then state the smallest safe rollout unit |
| Existing single-account estate moving into Organizations | `organization-structure`, `blast radius` | Focus on migration sequencing, shared-services placement, and how guardrails will land without locking out current operators |
| Control Tower versus lighter custom control-plane direction | `governance`, `operations` | State what managed guardrails buy, what flexibility is lost, and where current-fact validation is required before committing |

### Identity or delegated-access choice

| Situation | Frame first | Recommendation shape |
| --- | --- | --- |
| Central team needs day-to-day operation of an integrated service | `identity and access`, `governance` | Compare delegated administrator patterns against management-account operation, then call out the trust and audit implications |
| Workload teams need cross-account delivery access | `identity and access`, `blast radius` | Compare direct broad roles against narrower environment-scoped roles and name the rollback impact if trust is too wide |
| Federation model is still undecided | `governance`, `compliance` | Keep the answer at trust-boundary and operating-model level, not IdP implementation detail |

### Cost-sensitive platform choice

| Situation | Frame first | Recommendation shape |
| --- | --- | --- |
| Shared services could live centrally or per account | `FinOps`, `operations` | Compare central efficiency against tenant isolation and operational burden, then say when duplication is worth the spend |
| Multi-region posture is being considered mainly for resilience | `FinOps`, `BC/DR` | Make the continuity target explicit before recommending the extra cost or complexity |
| Organization-wide baseline tooling is under review | `FinOps`, `maintainability` | Compare managed-service convenience against steady-state platform ownership cost |

## Decision note pattern

Use this when the question is too consequential for a quick answer but does not need a full deep analysis.

1. Decision statement: what AWS choice is being made.
2. Assumptions: what current state, constraints, or timelines the recommendation depends on.
3. Viable options: usually two or three realistic AWS-local paths.
4. Recommendation: which option wins and why.
5. Tradeoffs and blast radius: what gets better, what gets harder, and what is hard to reverse.
6. Validation note: what current-fact check, proof, or next-owner handoff is still required.

## When to stay quick answer versus upgrade to a decision note

| Stay in `Quick answer` when | Upgrade to `Decision note` when |
| --- | --- |
| One option is clearly better and the downside is local | At least two AWS-local options are still viable |
| The choice does not alter the organization, trust, or recovery posture | The choice changes account layout, delegated access, or continuity expectations |
| The answer can stay within one lens without hiding material risk | A second lens changes the recommendation or the risk statement |
| Freshness is not the deciding factor | Current AWS behavior, support boundaries, or limits could change the outcome |
