---
name: internal-aws-strategic
description: Use when the user needs high-level AWS platform decision support or tradeoff framing before implementation, and the next step is not yet structure, governance, operations, or code delivery.
---

# Internal AWS Strategic

Use this skill when the main need is to reason about an AWS decision before implementation.

This is a strategic support skill. It helps frame the decision, compare realistic options, expose tradeoffs, and recommend a direction. It does not implement the change and it does not choose Terraform, Python, or Bash on behalf of the user.

## When to use

- The user needs AWS decision support before execution.
- Multiple AWS approaches are credible and tradeoffs matter.
- The user wants a recommendation grounded in current AWS guidance.
- The user wants high-level support for platform, control-plane, governance, resilience, cost, or operational decisions.

## When not to use

- The task is already a clear implementation change.
- The user only needs Terraform, Python, Bash, IAM, or operations implementation detail.
- The task is purely post-rollout validation or evidence gathering.
- The request is narrow and operational with no real decision to frame.

## Main domains covered

- platform and control-plane decision framing
- AWS best-practice and design guidance
- organizational and account-model implications at decision level
- governance and identity implications at decision level
- operational implications at decision level
- resilience and continuity implications at decision level
- cost-value and FinOps implications at decision level

## Optional lens activation

Do not load every lens by default.

Use only the minimum set of lenses needed for the request. If the user explicitly names one or more lenses, prioritize only those. If the user does not name lenses, infer the smallest useful set.

Available lenses include:

- security
- identity and access
- organization-structure
- governance
- operations
- monitoring and observability
- BC/DR
- FinOps
- compliance
- rollout and rollback
- blast radius
- maintainability

Rules:

- Start narrow.
- Expand only when the request is broad, risky, or ambiguous.
- If another lens would materially improve the recommendation, suggest it briefly instead of forcing it.
- Keep the active lenses explicit when more than one is in play.

Load `references/lens-playbook.md` when the user wants a deeper framing aid or when the choice of lenses is not obvious.

## Optional BC/DR lens

BC/DR is optional.

Activate it only when:

- the user asks about resilience, backup, recovery, failover, RTO, RPO, or multi-region design
- the decision has clear continuity implications
- the recommendation would be materially incomplete without it

If BC/DR seems relevant but is not requested, suggest it as an optional lens instead of forcing it.

## Use of current documentation

Use `internal-aws-mcp-research` when the answer depends on current AWS documentation, service behavior, IAM semantics, support boundaries, limits, or updated best-practice guidance.

Do not invoke research by default for stable, generic reasoning. Use it when freshness materially affects the answer.

## Mandatory behavior

- Identify the decision first, not the implementation tool.
- Make assumptions explicit.
- Compare realistic options, not strawmen.
- Keep tradeoffs concrete.
- Surface material risk, blast radius, and reversibility when relevant.
- Include cost-value considerations when they matter to the decision.
- Stay proportional to the size of the question.

## Adaptive output modes

Choose the lightest output that fits the request.

### Quick answer

Use for narrow asks.

Include:

- direct recommendation
- short rationale
- optional risk or follow-up note

### Decision note

Use for normal strategic support.

Include:

- decision statement
- key options or tradeoff
- recommended direction
- main risk or validation note

### Deep analysis

Use only for broad, ambiguous, high-risk, or explicitly detailed requests.

Include:

- context and assumptions
- options considered
- active lenses used
- recommendation and why it wins
- main risks and blast radius
- validation or follow-up path

## Relationship to adjacent skills

- `antigravity-aws-cost-optimizer`
  Use as depth support when the strategic question becomes cost analysis, spend optimization, or FinOps estimation that needs AWS-specific billing and Cost Explorer guidance.
- `internal-aws-organization-structure`
  Use when the next need is account model, OU layout, delegated admin placement, network topology, or control-plane structure.
- `internal-aws-governance`
  Use when the next need is IAM model, SCP design, trust boundaries, federation, or guardrail definition.
- `internal-aws-operations`
  Use when the next need is monitoring, backup, recovery validation, reporting, audit evidence, preflight, or post-rollout checks.
- `internal-terraform`, `internal-script-python`, `internal-script-bash`
  Use when the decision is settled and implementation begins.

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Forcing a full multi-lens analysis for a small question | The answer gets heavy without improving the decision | Start with the smallest useful lens set and widen only if risk or ambiguity justifies it |
| Treating BC/DR as mandatory for every answer | Continuity concerns drown out the actual decision | Activate BC/DR only when recovery posture materially changes the recommendation |
| Recommending a direction without current-source verification when freshness matters | AWS support boundaries, limits, or service behavior may have changed | Call out the freshness dependency and route to `internal-aws-mcp-research` when it can change the decision |
| Confusing decision support with implementation guidance | The user loses the strategic framing they asked for | Keep the answer at decision level and hand off only after the direction is chosen |
| Expanding into tool or IaC selection when the user did not ask for it | The response drifts from AWS platform tradeoffs into execution detail | Keep the recommendation centered on the AWS choice, not the delivery tooling |
| Giving generic best-practice advice without context, tradeoff, or cost implication | Generic guidance is hard to act on and easy to misapply | Tie the recommendation to assumptions, viable options, and cost-value consequences |

## Validation

- Confirm the decision statement is explicit and narrow enough that the next owner is obvious.
- Confirm assumptions, active lenses, and the main tradeoff are named instead of implied.
- Confirm the recommendation includes reversibility or blast-radius guidance when the choice is hard to unwind.
- Confirm cost-value or operational impact is called out when it materially changes the recommendation.
- Confirm the answer states when freshness matters and whether `internal-aws-mcp-research` should be used.
