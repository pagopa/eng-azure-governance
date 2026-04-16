# GitHub Strategic Lens Playbook

Use this reference when the user wants more depth than the base skill should load by default.

## Common lens combinations

| Situation | Start with | Add only if needed |
| --- | --- | --- |
| Enterprise or repo-model choice | governance, maintainability | FinOps, BC/DR |
| Automation or integration choice | security, governance | runner model, blast radius |
| Copilot rollout or licensing choice | Copilot, FinOps | governance, compliance |
| Runner-platform decision | runner model, operations | FinOps, BC/DR |
| High-risk workflow or release change | rollout and rollback, blast radius | operations, governance |

## Signals that another lens should be suggested

- Spend or licensing could materially change the recommendation: suggest `FinOps`
- The choice changes permissions, Apps, rulesets, OIDC, or environments: suggest `governance`
- The rollout adds runner, audit, or validation burden: suggest `operations`
- The decision changes delivery continuity or recovery posture: suggest `BC/DR`
- The choice materially affects developer workflow or repo shape: suggest `maintainability`

## Depth control

- Stay in `Quick answer` mode when one option is clearly better and the user asked a narrow question.
- Upgrade to `Decision note` when at least two viable options exist.
- Upgrade to `Deep analysis` only when the user asks for it or the risk profile justifies it.

## Worked GitHub decision shapes

### Enterprise or repo-model choice

| Situation | Frame first | Recommendation shape |
| --- | --- | --- |
| Team is choosing mono-repo versus multi-repo | `maintainability`, `governance` | Compare developer workflow, ruleset scope, and ownership blast radius before recommending a model |
| Organization layout or repository ownership is unclear | `governance`, `blast radius` | Compare centralized versus delegated ownership and name the smallest safe rollout unit |
| Enterprise-level GitHub rollout is still forming | `governance`, `FinOps` | Focus on entitlement, operating boundaries, and support model before implementation detail |

### Apps, automation trust, or runner choice

| Situation | Frame first | Recommendation shape |
| --- | --- | --- |
| Automation could run as GitHub App, Actions token, or external integration | `security`, `governance` | Compare trust boundary, permission surface, and operational burden, then say which path is easier to audit |
| Runner platform is undecided | `runner model`, `operations` | Compare managed convenience against fleet ownership and continuity expectations |
| OIDC posture is being considered mainly to remove secrets | `security`, `governance` | Keep trust design, scope, and rollout risk explicit before implementation details |

### Copilot rollout or licensing choice

| Situation | Frame first | Recommendation shape |
| --- | --- | --- |
| Copilot rollout is limited by budget or policy | `Copilot`, `FinOps` | Compare broad rollout against staged enablement and name the governance implications |
| A team wants to pilot Copilot features in a narrower scope | `Copilot`, `governance` | State how policy, visibility, and exception handling will be kept explicit |
| Enterprise wants a platform-wide enablement direction | `Copilot`, `compliance` | Keep entitlement decisions separate from repo-permission design |

## Decision note pattern

Use this when the question is too consequential for a quick answer but does not need a full deep analysis.

1. Decision statement: what GitHub choice is being made.
2. Assumptions: what current org model, runner posture, compliance needs, or licensing limits matter.
3. Viable options: usually two or three realistic GitHub-local paths.
4. Recommendation: which option wins and why.
5. Tradeoffs and blast radius: what gets better, what gets harder, and what is difficult to reverse.
6. Validation note: which current fact, proof, or handoff is still required.

## When to stay quick answer versus upgrade to a decision note

| Stay in `Quick answer` when | Upgrade to `Decision note` when |
| --- | --- |
| One option is clearly better and the downside is local | At least two GitHub-local options are still viable |
| The choice does not alter trust, continuity, or repo ownership posture | The choice changes repo model, Apps trust, runner model, or Copilot posture |
| The answer can stay within one lens without hiding material risk | A second lens changes the recommendation or the risk statement |
| Freshness is not the deciding factor | Current GitHub behavior, permissions, or product limits could change the outcome |
