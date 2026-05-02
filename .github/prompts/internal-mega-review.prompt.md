---
name: "internal-mega-review"
agent: "agent"
description: "Run a complete advisor-only mega review for one or more repositories and write split English analysis under each repo tmp/"
argument-hint: "Repository paths or names; optional focus and constraints; retained output is English"
---

<!-- markdownlint-disable-file MD041 -->

Repositories to review:
${input:repositories:List one or more repository names or paths. Use one per line when possible.}

Optional focus areas:
${input:focus:Optional focus such as security, governance, architecture, testing, automation, documentation, AI-readiness, or migration risk}

Optional constraints or exclusions:
${input:constraints:Optional non-negotiables, exclusions, prior findings to preserve, or rollout concerns}

Output language:
${input:language:Match chat language unless explicitly overridden. If you want to force one, write Italian or English.}

Retained analysis content, headings, tables, and artifact filenames must stay in English.

Use these standards-repository sources first for governance, evidence, and split-output discipline:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-instructions.md](../copilot-instructions.md)
- [.github/INVENTORY.md](../INVENTORY.md)
- [.github/agents/internal-planning-leader.agent.md](../agents/internal-planning-leader.agent.md)
- [.github/agents/internal-critical-master.agent.md](../agents/internal-critical-master.agent.md)
- [.github/skills/internal-writing-plans/SKILL.md](../skills/internal-writing-plans/SKILL.md)

For this mega-review prompt, the English retained artifact contract below overrides any legacy non-English filename examples in those sources.

Then run a complete, analysis-only mega review with these rules.

## 1. Mission

Review one or more repositories as a pragmatic technical advisor.

- Do not apply fixes.
- Do not edit production files.
- Do not rename, move, or delete real repository assets.
- Write analysis artifacts only under `tmp/`.
- Keep the output concise, operational, evidence-based, written in English, and ready to guide later implementation work.

## 2. Repository Resolution

For each item in `repositories`:

1. Resolve it to a real repository path in the current workspace or obvious sibling path.
2. If the path is ambiguous or missing, stop and ask only for the unresolved repository.
3. Treat each resolved repository independently before producing any cross-repo synthesis.

## 3. Output Locations

For each target repository, write the retained analysis under:

- `<repo>/tmp/superpowers/mega-review/`

If more than one repository is reviewed, also create a global cross-repo package under:

- `tmp/superpowers/mega-review-global/`

If the target `tmp/superpowers/mega-review/` folder already exists:

- Preserve the previous analysis.
- Do not rewrite it wholesale.
- Add only missing coverage, corrections, or newly discovered findings in a separate numbered file such as `04-review-addendum.md`.
- Update `01-executive-summary.md` only when the executive summary is materially outdated.
- Do not create new non-English filenames. If a prior package uses legacy non-English filenames, preserve those files and continue with English-named delta files unless the user explicitly asks for migration.

If no prior review exists, create a fresh split review package.

## 4. Required Method

For each repository:

1. Start with a compact inventory before judging the repository.
2. Derive the technology stack only from repository evidence on disk.
3. Adapt the review to the observed stack and domain.
4. If the repository contains technologies, frameworks, or tooling not explicitly anticipated here, extend the review to cover them from first principles instead of skipping them.
5. Never invent technologies, workflows, or controls that are not present.
6. Prefer repository evidence over assumptions, and explicit uncertainty over false confidence.

## 5. Inventory First

Before findings, produce a compact repository inventory covering what is actually present, for example:

- Languages
- Frameworks and runtime tooling
- IaC tooling such as Terraform, Terragrunt, CloudFormation, Pulumi, Helm, Kubernetes manifests, Rego, policy files, or equivalent
- CI/CD systems and workflow triggers
- Security controls and scanning surfaces
- Test and validation surfaces
- Documentation and runbooks
- Governance and audit artifacts
- AI-facing files such as `AGENTS.md`, prompt files, instructions, skills, memory, or repository-specific agent guidance
- Repository purpose and likely owner, if inferable from evidence

If an area is not present or not verifiable, say so.

## 6. Review Dimensions

For each repository, review at least these dimensions when relevant to the observed stack:

- Security and least privilege
- Architecture and design clarity
- Code and script quality
- Automation and CI/CD
- Testing and validation
- Documentation and operational readiness
- Governance and auditability
- AI-readiness
- Cleanup, dead assets, drift, and standardization opportunities

Also adapt to domain-specific concerns such as IAM, RBAC, policy-as-code, cloud governance, FinOps, GitHub org governance, platform operations, or repo-governance when those are actually present.

## 7. Evidence Rule

Every finding must cite concrete evidence such as:

- A specific path
- A specific workflow
- A repeated pattern observed in files or directories
- A missing but expected validation surface relative to the detected stack
- An explicit contrast with another reviewed repository when doing cross-repo analysis

If a claim cannot be tied to concrete evidence, move it to open questions or blockers instead of classifying it as a finding.

## 8. Finding Format

For each material finding, use this structure:

### Finding Title

- Severity: Critical | Medium | Low
- Category: Security | Architecture | Automation | Testing | Documentation | Governance | AI-readiness | Cleanup
- Classification: Must | Should | Could | Won't for now
- Evidence: specific file, directory, workflow, or repeated pattern
- Problem: what is wrong
- Impact: why it matters
- Proposed action: what to do later
- Estimated effort: S | M | L
- Invasiveness: low | medium | high
- Less invasive alternative: if applicable

## 9. Required Output Shape Per Repository

Use split numbered files, not one monolithic document.

Minimum retained output per repository:

- `01-executive-summary.md`
- `02-inventory-and-current-state.md`
- `03-findings-and-backlog.md`
- `open-questions-and-blockers.md`

If the repository already has a retained review package, prefer a complement file such as:

- `04-review-addendum.md`

`01-executive-summary.md` must always exist as the entrypoint for a fresh review package.

Minimum coverage inside the split files:

1. Executive summary
2. Repository inventory
3. Repository purpose and current state
4. Critical findings
5. Medium findings
6. Low findings
7. Security review
8. Architecture and design review
9. Automation and CI/CD review
10. Testing and validation review
11. Documentation and operational readiness
12. Enterprise governance and auditability
13. AI-readiness review
14. Files and structure actions table
15. Prioritized remediation backlog
16. Quick wins
17. Strategic improvements when justified
18. Open questions and blockers

If a section has no meaningful issue, say: `No relevant finding observed.`

## 10. Required Tables

Use these tables where relevant.

Files and structure actions:

| Action | File or directory | Reason | Risk | Effort | Notes |
|---|---|---|---|---|---|

Allowed actions:

- keep
- delete
- merge
- split
- rename
- compress
- move
- create
- automate
- standardize

Prioritized remediation backlog:

| Priority | Classification | Finding | Category | Impact | Effort | Invasiveness | Risk if ignored | Expected benefit | Files or directories | Proposed action |
|---|---|---|---|---|---|---|---|---|---|---|

Allowed priorities:

- P0 = critical risk or major blocker
- P1 = high value or high risk
- P2 = important but not urgent
- P3 = cleanup or optional optimization

## 11. Cross-Repo Output When Reviewing More Than One Repository

If more than one repository is in scope, also produce a global split review under `tmp/superpowers/mega-review-global/`.

Minimum global output:

- `01-executive-summary.md`
- `02-consistency-cross-repo.md`
- `03-security-and-automation-gaps.md`
- `04-global-roadmap.md`
- `05-global-ai-readiness.md`
- `06-recommended-global-standard.md`
- `open-questions-and-blockers.md`

Optional when complementing an existing global package:

- `07-review-addendum.md`
- `08-critical-master-consistency-gate.md`

Global review coverage must include:

1. Executive summary
2. Global maturity matrix
3. Cross-repo consistency
4. Common security gaps
5. Common automation opportunities
6. Standardization candidates
7. Provider-specific or domain-specific differences that should remain local
8. Global AI-readiness assessment
9. Recommended repository standard
10. Global prioritized roadmap

Use this maturity matrix:

| Repo | Security maturity | Automation maturity | Testing maturity | Documentation maturity | Governance maturity | AI-readiness | Main gap | Top quick win | Top strategic move |
|---|---|---|---|---|---|---|---|---|---|

Use this roadmap table:

| Priority | Classification | Initiative | Repositories involved | Problem solved | Benefit | Effort | Invasiveness | First step |
|---|---|---|---|---|---|---|---|---|

## 12. Review Discipline

- Be severe but useful.
- Prefer pragmatic changes over aesthetic refactors.
- Recommend invasive changes only when the benefit is clearly justified.
- For every invasive proposal, explain why it is necessary, the less invasive option, the risk of doing it, the risk of not doing it, and the estimated effort.
- Do not overuse `Must`.
- Do not confuse temporary uncertainty with a verified problem.

## 13. Existing Analysis Handling

If the repository already contains prior analysis under `tmp/`:

- Read it first.
- Preserve what is still valid.
- Only add missing sections, corrected evidence, or newly observed findings.
- Avoid duplicating the same backlog item unless the evidence has materially changed.
- Keep newly created retained artifacts in English even when prior retained analysis used another language or legacy filenames.

## 14. Final Consistency Gate

Before finishing, validate the resulting analysis against the challenge posture defined in:

- [.github/agents/internal-critical-master.agent.md](../agents/internal-critical-master.agent.md)

Run a brief consistency gate that answers:

1. What in the final review is most likely correct?
2. What is most likely incorrect, contradictory, overstated, or insufficiently verified?
3. Which findings should be downgraded, reframed, or moved to open questions?

If useful, save that gate as a retained artifact in the global package or in the reviewed repository package.

## 15. Final Quality Bar

Before stopping, verify that the retained output is:

- Concrete
- Verifiable
- Non-generic
- Non-destructive
- Adapted to the observed repositories and stacks
- Split into multiple files
- Written with English retained content and filenames
- Useful for follow-up implementation work
- Explicit about impact, priority, effort, and uncertainty

If a repository cannot support a complete review because key evidence is missing, say exactly what is not verifiable from the repository and continue with the parts that are verifiable.
