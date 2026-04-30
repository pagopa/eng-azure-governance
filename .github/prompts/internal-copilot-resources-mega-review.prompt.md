---
name: "internal-copilot-resources-mega-review"
agent: "agent"
description: "Run a decision-focused mega review of Copilot and AI repository resources with a mandatory pre-analysis control pass, evidence discipline, wrapper-aware overlap checks, and a final completeness pass so nothing important is missed"
---

<!-- markdownlint-disable-file MD041 -->

Primary goal:
${input:goal:Describe the repository, the review goal, and the main reason for the mega review}

Paths or asset families in scope:
${input:scope:List the folders, files, or asset families to inspect}

Target runtimes:
${input:runtimes:List the main runtimes, for example Claude Opus 4.7, ChatGPT 5.5, and GitHub Copilot}

Known local architecture assumptions:
${input:assumptions:List important repo-specific assumptions, such as internal wrappers around imported resources}

Constraints and exclusions:
${input:constraints:List non-negotiables, rollout constraints, things that must not be modified, or evidence limits}

Use these repository sources first:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-instructions.md](../copilot-instructions.md)
- [.github/INVENTORY.md](../INVENTORY.md)
- [INTERNAL_CONTRACT.md](../../INTERNAL_CONTRACT.md)
- [LESSONS_LEARNED.md](../../LESSONS_LEARNED.md)
- [.github/agents/internal-planning-leader.agent.md](../agents/internal-planning-leader.agent.md)

Language rules:

- Write the final analysis and summary in the language of the current chat.
- If the current chat language is ambiguous or mixed, prefer Italian.
- Keep file paths, enum values, and evidence labels exactly as requested.

Mandatory control pass before any analysis:

1. Read `AGENTS.md` and `.github/copilot-instructions.md` before opening the detailed review.
2. Build an internal coverage checklist for every explicit requirement in this prompt.
3. Verify which asset families actually exist on disk before making recommendations: agents, skills, instructions, prompt files, scripts, docs, memory, inventory, governance files.
4. Before calling anything a duplicate, compare contents and roles. Check whether one file is a thin wrapper, convenience entry point, repository-owned internal wrapper, imported depth asset, or sync helper.
5. When an imported asset overlaps with a domain already covered by an `internal-*` resource, use three-way decision logic: `KEEP`, `WRAP`, or `REVIEW/RETIRE`. Do not collapse the decision to keep-or-delete.
6. If the retained analysis will span multiple files, decide up front where each requested output section will live so the final report has full coverage.
7. Keep a running list of anything that is not fully proven. Those items must end up in the low-evidence or open-questions sections, not in strong recommendations.
8. Treat the questions below as an internal checklist, not as a mechanical final structure.

Review objective:

Run a decision-focused mega review of the repository as the source of truth for AI resources:

- agents
- skills
- instructions
- prompt files
- scripts
- docs
- memory
- inventory
- governance files

The purpose is not to modify the repository assets themselves. The purpose is to produce an evidence-based and action-oriented analysis that clarifies what should be:

- kept
- removed
- merged
- split
- renamed
- compressed
- moved
- created
- automated

Analysis-only rules:

- Do not patch, rewrite, or refactor existing repository assets.
- Only write the analysis under `tmp/`.
- If the retained analysis spans multiple macro-categories, use `tmp/superpowers/<clear-task-name>/` and split it into numbered Markdown files starting with `01-riassunto-esecutivo.md`. Keep open questions in `dubbi-e-domande.md`.
- If a single concise Markdown file is enough, keep it directly under `tmp/`.

Decision-review rules:

- Do not produce an encyclopedic review.
- Include only real problems, important tradeoffs, recommended decisions, blocking uncertainties, and high-ROI quick wins.
- If a resource has no meaningful problem, do not spend report space on it unless it needs a `KEEP` line in the decision table.

Evidence standard:

- `ALTA`: supported by specific files and direct comparison.
- `MEDIA`: supported by patterns observed in the repository.
- `BASSA`: plausible hypothesis that is not fully verifiable.
- `DA VERIFICARE`: requires manual confirmation.

Evidence rules:

- Do not propose `DELETE`, `MERGE`, `MOVE`, `SPLIT`, or `CREATE` with `BASSA` evidence.
- In those cases use `REVIEW` or `DA VERIFICARE`.
- Always cite at least one real file for `MERGE`, `DELETE`, `MOVE`, `SPLIT`, `CREATE`, or `COMPRESS`.
- Distinguish explicitly between `EVIDENCE`, `INFERENCE`, `ASSUMPTION`, and `UNKNOWN` in the analysis.
- Do not turn `ASSUMPTION` or `UNKNOWN` into strong recommendations.

False-positive protection:

- Do not call resources duplicated just because they look similar.
- Before calling something a duplicate, verify real differences in trigger, scope, audience, target model, workflow phase, abstraction level, token cost, frequency of use, operational responsibility, and position in the repository hierarchy.
- Classify every overlap as one of: `DUPLICAZIONE REALE`, `SOVRAPPOSIZIONE ACCETTABILE`, `SOVRAPPOSIZIONE INTENZIONALE`, `DA VERIFICARE`.

Prudence rules:

- Do not suggest merge, deletion, or relocation just to reduce file count.
- A resource should be merged, removed, or moved only if it lacks a distinct trigger, lacks a distinct responsibility, does not improve the ChatGPT 5.5 plus Copilot workflow, increases ambiguity, increases maintenance, increases token cost without proportional benefit, duplicates an existing resource, or conflicts with `AGENTS.md` or `.github/copilot-instructions.md`.
- If the benefit is unclear, use `REVIEW` or `DA VERIFICARE`, not `DELETE`.

Runtime target:

- Claude Opus 4.7 for critical review, structured analysis, and deep reasoning.
- ChatGPT 5.5 for analysis, design, strategy, and evolutionary iteration.
- GitHub Copilot for operational support inside the IDE and repository.
- Possible reuse of some resources across ChatGPT 5.5 and Copilot.

Use the following checklist internally.

1. Agents

- Are the existing agents necessary?
- Which agents can be merged?
- Which agents are redundant?
- Which agents are too broad?
- Which agents are too specific?
- Which agents should become skills?
- Which agents should become prompt files?
- Which agents should be removed?
- Which agents are missing?
- Is a router or orchestrator needed?
- Should a router only suggest the next agent, or also prepare the operating brief?
- Are there agents that should be separated into planner, executor, and reviewer?
- Are the agent names clear?
- Do the agents respect the hierarchy described in `AGENTS.md`?
- Are the agents useful in the ChatGPT 5.5 to Copilot workflow?

1. Instructions

- Are they partitioned correctly?
- Do they activate on the right paths?
- Do they overlap?
- Are some instructions never activated?
- Are they too generic?
- Are they too long?
- Do they contain rules that belong in skills?
- Do they contain rules that belong in prompts?
- Do they duplicate `copilot-instructions.md`?
- Do they respect the model described in `copilot-instructions.md`?
- Do they help Copilot without bloating context too much?

1. Skills

- Are they partitioned correctly?
- Do they have clear triggers?
- Are they useful?
- Are they too large?
- Are they too small?
- Are they redundant?
- Are they optimized for token ROI?
- Should any skills be merged?
- Should any skills be removed?
- Should any skills become instructions?
- Should any skills become prompts?
- Are any high-ROI skills missing?
- Do the skills connect well to the agents?
- Do the skills support ChatGPT 5.5 and or Copilot well?

1. Prompt files

- Are the prompts useful?
- Are there too many or too few?
- Are they reusable?
- Do they have clear inputs?
- Do they have clear outputs?
- Do they have clear constraints?
- Do they have versioning?
- Should any prompts become skills?
- Should any prompts become instructions?
- Are any high-ROI prompts missing?
- Do the prompts help the ChatGPT 5.5 to Copilot handoff?

1. Scripts

- Are they still necessary?
- Are they simple?
- Are they fast?
- Are they documented?
- Are they idempotent?
- Do they have adequate error handling?
- Can they generate inventory, maps, or reports?
- Can they validate agents, skills, instructions, and prompts?
- Which scripts would immediately improve productivity?
- Which scripts would help maintain coherence between ChatGPT 5.5 and Copilot?

1. Docs, memory, and inventory

- Is there a clear map of the AI resources?
- Is there a reliable inventory?
- Is there a `docs/ai-memory/` or equivalent?
- Is there a decision log?
- Is there a matrix for agent, skill, prompt, and instruction?
- Is there a guide for using the repo with ChatGPT 5.5 plus Copilot?
- Is there a guide for updating the repo without breaking it?
- Are any documents obsolete or misleading?
- Does the memory layer reduce token use and ambiguity, or add noise?

1. Token economy

- Where are tokens being wasted?
- What gets loaded too often?
- What should be lazy-loaded?
- What belongs in minimal always-on instructions?
- What belongs in on-demand skills?
- What belongs in prompt files?
- What belongs in docs?
- Where are the expensive duplications?
- Which resources should be compressed?
- Which resources truly reduce cost in the ChatGPT 5.5 plus Copilot workflow?

1. Productivity

- What truly accelerates the work?
- What creates friction?
- What requires too much maintenance?
- Where is the repository over-engineered?
- Where is it under-invested?
- Where is automation missing?
- Which five quick interventions would deliver the highest ROI?
- Which three things should stop?
- Which three things should start?
- What improves the analysis to implementation to verification flow?

Decision criteria for every resource:

- Necessity
- Uniqueness
- Clarity
- Activation timing
- Token ROI
- Maintainability
- Composability
- Risk
- Productivity impact
- Hierarchical coherence with `AGENTS.md` and `copilot-instructions.md`
- Runtime fit for ChatGPT 5.5, Copilot, or both
- Evidence quality

Required output structure:

1. Executive summary

- Maximum 10 lines.
- State the real repository condition: healthy, promising but messy, redundant, too complex, fragile, or well structured but improvable.

1. Observed mental model

- Maximum 15 lines.
- Summarize what you learned from `AGENTS.md` and `.github/copilot-instructions.md`.
- Explain the effective hierarchy between `copilot-instructions.md`, `AGENTS.md`, instructions, agents, skills, prompts, scripts, and docs or memory.

1. Main diagnosis

- Split into: what works, what is redundant, what is fragile, what costs too many tokens, what blocks productivity, and what is missing.
- Maximum 3 bullets per section.

1. Decision table

- Single table with columns: `Area | Resource | Status | Evidence | Problem | Decision | Priority`.
- Allowed statuses: `KEEP`, `MERGE`, `SPLIT`, `DELETE`, `RENAME`, `MOVE`, `CREATE`, `COMPRESS`, `REVIEW`, `WRAP`.
- Allowed evidence: `ALTA`, `MEDIA`, `BASSA`, `DA VERIFICARE`.
- Priorities: `P0`, `P1`, `P2`, `P3`.

1. Detected overlaps

- Table with columns: `Resources involved | Type | Evidence | Assessment | Proposed action`.
- Allowed types: `DUPLICAZIONE REALE`, `SOVRAPPOSIZIONE ACCETTABILE`, `SOVRAPPOSIZIONE INTENZIONALE`, `DA VERIFICARE`.

1. Low-evidence recommendations

- Separate all `BASSA` or `DA VERIFICARE` recommendations.
- Use the exact format: `Recommendation | Why it is not certain | What to verify`.
- Do not include destructive actions such as `DELETE`, `MERGE`, `MOVE`, or `SPLIT` in this section.

1. Quick wins

- Maximum 10.
- Table format: `Quick win | Evidence | Impact | Effort | Why it is worth doing`.

1. Recommended actions

- Split into: `Do now`, `Do later`, `Do not do now`.
- Maximum 5 items per subsection.
- The `Do now` subsection may only contain `ALTA` or `MEDIA` evidence actions.

1. Recommended roadmap

- Advice only, not a binding plan.
- Split into: `Cleanup`, `Rationalization`, `Automation`, `Governance`, `Evolution`.
- Maximum 3 bullets per phase.

1. Proposed target architecture

- Propose a realistic target repository structure.
- Explain only the differences versus the current state.

1. Future rule

- Table with columns: `Type | When to create it | When to avoid it`.
- Cover: agent, skill, instruction, prompt, script, doc or memory.

1. Final critique

- Maximum 10 lines.
- State clearly: what is being done well, what is likely overcomplicated, what is killing productivity, and what the best next step is.

Mandatory completeness pass before the final answer:

1. Re-open every retained analysis file you wrote.
1. Check that all 12 required output sections exist.
1. Check that every explicit checklist family above is either answered or explicitly marked as not verifiable.
1. Check skill coverage especially carefully: partitioning, triggers, usefulness, size, redundancy, token ROI, merge or removal candidates, conversion to instructions or prompts, missing high-ROI skills, linkage to agents, and runtime fit.
1. If prompt files exist, verify that inputs, outputs, constraints, versioning, reuse value, and missing prompt opportunities are covered explicitly.
1. If scripts exist, verify that necessity, simplicity, speed, documentation, idempotence, error handling, validation value, and automation opportunities are covered explicitly.
1. Check that every strong recommendation cites at least one real file and has `ALTA` or `MEDIA` evidence.
1. Check that the low-evidence section contains no destructive actions.
1. Check that every apparent duplicate or overlap was tested against thin-wrapper, convenience-entry-point, and internal-wrapper possibilities before being called a real duplication.
1. If any gap remains, update the retained analysis first and only then present the final summary.

Final operating constraints:

- Be concise.
- Analysis only.
- Do not modify repository assets.
- Do not create repository patches.
- Do not rewrite existing resources.
- Prefer small, concrete, high-ROI actions.
- Every strong recommendation needs a practical reason and `ALTA` or `MEDIA` evidence.
- Do not propose new technology before diagnosing the existing repository correctly.
