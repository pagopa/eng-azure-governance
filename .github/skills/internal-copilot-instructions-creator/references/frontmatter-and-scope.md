# Frontmatter and Scope

Load this file when drafting a new `.instructions.md` file or changing an existing file's trigger scope.

## File Identity

- Keep repository-owned instruction files under `.github/instructions/`.
- Use lowercase hyphenated filenames ending in `.instructions.md`.

## Required Frontmatter

Use only:

```yaml
---
description: "What the instruction covers and when it applies"
applyTo: "**/*.ext"
---
```

## `description` Guidance

- State the purpose and the scope in one sentence.
- Keep it concrete enough that a maintainer can tell why the file exists.
- Match nearby quoting style; do not invent extra metadata fields.

## `applyTo` Guidance

| Goal | Prefer | Avoid |
| --- | --- | --- |
| One stack in one repo area | `src/**/*.py` or `**/*.java` when the scope is truly broad | `**` or mixed patterns that catch unrelated files |
| One framework convention | Framework-specific directories or filename families | All files of a language when the framework is only one subset |
| Multiple related families | A short comma-separated list of specific globs | Long catch-all lists added "just in case" |

## Scope Anti-Patterns

- Broad globs that fire on routine edits with no relevant guidance.
- Framework-specific instructions attached to every file of a language.
- Meta instructions that author other instructions but auto-load on every instruction file unless that authoring workflow is actually intended.
- Path patterns that overlap heavily with a stronger internal instruction without adding a distinct boundary.
