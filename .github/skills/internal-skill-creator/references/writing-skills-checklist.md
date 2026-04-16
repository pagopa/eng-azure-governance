# Writing Skills Checklist

Load this reference when creating a new repository-owned skill or materially revising an existing one.

This is a local distilled checklist informed by `writing-skills`. It exists to keep the wrapper self-contained without cloning the upstream bundle.

## Core posture

- Treat a skill as a reusable guide for future agents, not as a narrative about one past task.
- Iron law: do not create or materially revise a skill without first seeing the failure it must fix.
- Do not create or materially revise a skill without first observing the failure, miss, or ambiguity it must fix.
- Use the same proof standard for edits as for new skills.
- Check frontmatter validity before reviewing route quality or body wording. Structural breakage outranks content cleanup.
- Compare the target skill against the closest neighboring owners before deciding the fix. Route quality is a lane-level property.

## Discovery and retrieval

- Keep `description:` focused on when the skill should load.
- Avoid describing the workflow in `description:`. That creates shortcuts and weakens body retrieval.
- Make `description:` read like realistic user intent, not like a capability summary or mini playbook.
- If `description:` names too many adjacent lanes, treat it as overlap until proven otherwise.
- Use words an agent would actually search for: symptoms, overlaps, file paths, task verbs, and validation terms.
- Prefer direct action-shaped names when naming a new skill.

## Tightening strategy

- Prefer the smallest fix that solves the miss: one description tighten, one boundary note, or one misleading phrase removed.
- Do not rewrite a long body just because it is long. Rewrite only when it duplicates the route, duplicates another owner, or keeps reference material inline.
- A clean "tighten" outcome is often better than expanding the skill.

## Token discipline

- Keep `SKILL.md` lean and move deeper material into `references/` or reusable tools only when justified.
- Preserve a working `description:` during token cuts unless the baseline shows routing is wrong.
- Cross-reference reusable material instead of restating it.
- Prefer moving static lookup tables, starter templates, and detailed taxonomies into `references/`.
- Prefer new `references/` over new `scripts/` unless the workflow is deterministic, repeated, and execution-heavy.
- Prefer one strong example over several repetitive ones.

## Test posture

- Run a baseline scenario without the skill or before the edit and capture the failure.
- Re-run the same scenario with the skill after the change.
- Re-run at least one neighboring-owner scenario when the edit changes routing or boundary wording.
- Add a misuse, pressure, or counterexample test based on the skill type.

## Skill-type checks

- Discipline: test pressure, loopholes, and rationalizations.
- Technique: test failure case, success case, and one misuse case.
- Pattern: test recognition, correct use, and counterexample boundaries.
- Reference: test retrieval, correct application, and common gaps.

## Red flags

- "This is obvious."
- "It is only wording."
- "We can test later."
- "This should probably become a new skill."
- "I already know what the skill should say."

When one of these appears, stop and re-check the baseline and boundary.
