---
name: internal-azure-strategic
description: Use when the user needs high-level Azure platform decision support or tradeoff framing before implementation, and the next step is not yet structure, governance, operations, or code delivery.
---

# Internal Azure Strategic

Use this skill when the main need is to reason about an Azure decision before implementation.

This is a strategic support skill. It helps frame the decision, compare realistic options, expose tradeoffs, and recommend a direction. It does not implement the change and it does not choose Terraform, Python, or Bash on behalf of the user.

## When to use

- The user needs Azure decision support before execution.
- Multiple Azure approaches are credible and tradeoffs matter.
- The user wants a recommendation grounded in current Microsoft guidance.
- The user wants high-level support for platform, landing-zone, governance, resilience, cost, or operational decisions.

## When not to use

- The task is already a clear implementation change.
- The user only needs detailed RBAC, Policy, monitoring, backup, or automation implementation.
- The task is purely post-rollout validation or evidence gathering.
- The request is narrow and operational with no real decision to frame.

## Main domains covered

- platform and landing-zone decision framing
- Cloud Adoption Framework and Well-Architected guidance at decision level
- tenant, management-group, and subscription implications at decision level
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

- the user asks about resilience, backup, recovery, failover, RTO, RPO, or regional continuity
- the decision has clear continuity implications
- the recommendation would be materially incomplete without it

If BC/DR seems relevant but is not requested, suggest it as an optional lens instead of forcing it.

## Use of current documentation

Use current Microsoft documentation only when freshness materially affects the answer, especially for Azure service support, landing-zone guidance updates, Policy behavior, RBAC semantics, regional capability, or service limits.

Do not invoke current-doc research by default for stable, generic reasoning.

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

- `awesome-copilot-azure-pricing`
  Use as depth support when the strategic question becomes SKU pricing, spend estimation, or Azure-specific cost comparison that needs current pricing data.
- `internal-azure-organization-structure`
  Use when the next need is tenant hierarchy, management-group layout, subscription model, landing-zone placement, or platform topology.
- `internal-azure-governance`
  Use when the next need is RBAC model, managed identity boundaries, PIM/PAM posture, Policy design, or guardrail definition.
- `internal-azure-operations`
  Use when the next need is Azure Monitor, backup, Site Recovery validation, reporting, audit evidence, preflight, or post-rollout checks.
- `internal-terraform`, `internal-script-python`, `internal-script-bash`
  Use when the decision is settled and implementation begins.

## Anti-patterns

- forcing a full multi-lens analysis for a small question
- treating BC/DR as mandatory for every answer
- recommending a direction without current-source verification when freshness matters
- confusing decision support with implementation guidance
- expanding into tool selection when the user did not ask for it
- giving generic best-practice advice without context, tradeoff, or cost implication
