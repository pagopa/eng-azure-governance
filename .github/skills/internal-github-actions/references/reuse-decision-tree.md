# Reuse Decision Tree

Start with the smallest reusable unit that solves the repetition.

1. Is the repeated logic only one or two adjacent steps in a single workflow?
   Keep it inline.
2. Is the repeated logic mostly shell or language-specific commands that workflows call the same way?
   Extract a repository script and keep the workflow thin.
3. Does the reusable unit need its own jobs, runners, permissions, or concurrency?
   Use a reusable workflow.
4. Does the reusable unit stay inside one job and need to expose step outputs?
   Use a composite action.
5. Does the candidate reuse span several repositories or carry a compatibility contract for many callers?
   Prefer a composite action with documented inputs, outputs, and versioning.

Sanity checks before extracting:

- if the abstraction saves fewer than a couple of real call sites, keep it local
- if the reuse choice changes trust boundaries or secret flow, prefer the more explicit contract
- if reusable workflow and composite action both look plausible, default to the unit of reuse: jobs versus steps
