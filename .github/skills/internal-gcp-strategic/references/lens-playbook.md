# GCP Strategic Lens Playbook

Use this reference when the user wants more depth than the base skill should load by default.

## Common lens combinations

| Situation | Start with | Add only if needed |
| --- | --- | --- |
| Org or Shared VPC choice | organization-structure, governance | FinOps, BC/DR |
| Identity or workload access choice | identity and access, governance | blast radius, compliance |
| Rollout planning across folders or projects | rollout and rollback, blast radius | operations, BC/DR |
| Cost-sensitive platform decision | FinOps, maintainability | operations, governance |
| Resilience-sensitive design | BC/DR, operations | FinOps, blast radius |

## Signals that another lens should be suggested

- Cost could materially change the recommended option: suggest `FinOps`
- The decision changes org, folder, project, or Shared VPC layout: suggest `organization-structure`
- The choice changes IAM, workload identity, or Org Policy behavior: suggest `governance`
- The rollout adds monitoring, backup, inventory, or validation burden: suggest `operations`
- A failure would interrupt critical platform capability: suggest `BC/DR`

## Depth control

- Stay in `Quick answer` mode when one option is clearly better and the user asked a narrow question.
- Upgrade to `Decision note` when at least two viable options exist.
- Upgrade to `Deep analysis` only when the user asks for it or the risk profile justifies it.

## Worked GCP decision shapes

### Org or Shared VPC choice

| Situation | Frame first | Recommendation shape |
| --- | --- | --- |
| New platform needs clear enterprise segmentation | `organization-structure`, `governance` | Compare a simpler folder and project model against a more segmented operating model, then name the smallest safe rollout unit |
| Shared VPC ownership is undecided | `organization-structure`, `operations` | Compare central network ownership against product-aligned host projects and call out the operational burden tradeoff |
| Existing flat project estate needs stronger control boundaries | `organization-structure`, `blast radius` | Focus on migration sequencing, billing ownership, and how Org Policy inheritance will land safely |

### Identity or workload-access choice

| Situation | Frame first | Recommendation shape |
| --- | --- | --- |
| External delivery system needs access into GCP | `identity and access`, `governance` | Compare federation against key-based fallbacks and make the trust and audit boundary explicit |
| Service accounts have grown too broad | `governance`, `blast radius` | Compare shared service accounts against narrower purpose-built identities and name the rollback impact |
| Human and workload access patterns are being mixed | `identity and access`, `compliance` | Separate operator access from workload identity before recommending the control stack |

### Cost-sensitive platform choice

| Situation | Frame first | Recommendation shape |
| --- | --- | --- |
| Shared platform services could be centralized or duplicated per environment | `FinOps`, `operations` | Compare central efficiency against environment isolation and operational overhead |
| Multi-region posture is under consideration mainly for resilience | `FinOps`, `BC/DR` | Make the continuity target explicit before recommending the extra cost or complexity |
| Project-per-service versus larger shared projects is under review | `FinOps`, `maintainability` | Compare management overhead, isolation value, and chargeback clarity |

## Decision note pattern

Use this when the question is too consequential for a quick answer but does not need a full deep analysis.

1. Decision statement: what GCP choice is being made.
2. Assumptions: what current state, scale, or compliance constraints matter.
3. Viable options: usually two or three realistic GCP-local paths.
4. Recommendation: which option wins and why.
5. Tradeoffs and blast radius: what gets better, what gets harder, and what is difficult to reverse.
6. Validation note: which current fact, proof, or handoff is still required.

## When to stay quick answer versus upgrade to a decision note

| Stay in `Quick answer` when | Upgrade to `Decision note` when |
| --- | --- |
| One option is clearly better and the downside is local | At least two GCP-local options are still viable |
| The choice does not alter org, trust, or recovery posture | The choice changes folders, projects, Shared VPC layout, or continuity expectations |
| The answer can stay within one lens without hiding material risk | A second lens changes the recommendation or the risk statement |
| Freshness is not the deciding factor | Current Google Cloud behavior, support boundaries, or limits could change the outcome |
