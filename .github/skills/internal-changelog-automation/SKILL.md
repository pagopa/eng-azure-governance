---
name: internal-changelog-automation
description: Use when creating or improving changelog generation, release-note workflows, or repeatable release-documentation automation.
---

# Internal Changelog Automation

Use this skill when the repository needs deterministic release notes instead of ad hoc summaries.

This skill is guidance for designing or improving changelog automation. It does not imply that the current repository already has an active changelog generator wired into CI.

## When to use

- Design or improve changelog generation for releases or versioned governance changes.
- Create a repeatable release-note workflow from commits, pull requests, labels, or version boundaries.
- Tighten changelog discipline when the repository still relies on ad hoc manual summaries.

## Principles

- Prefer one canonical changelog flow for the repository.
- Separate human-facing release notes from raw commit history.
- Group changes by user impact, not by file touched.
- Keep automation deterministic and auditable.

## Recommended Structure

Use Keep a Changelog headings where possible:

- Added
- Changed
- Fixed
- Deprecated
- Removed
- Security

## Input Sources

- Conventional commit history
- Pull request titles and bodies
- Labels or release metadata
- Version boundaries or tags

## Workflow

1. Define the release range.
2. Collect commits and PR metadata.
3. Normalize entries into user-facing categories.
4. Remove noise such as merge-only or maintenance-only entries that do not matter to readers.
5. Produce release notes and update the changelog consistently.

## Semver Guidance

- Major: breaking changes or removals
- Minor: additive features
- Patch: fixes and low-risk maintenance

Call out versioning mismatches explicitly when the described changes and the release bump disagree.

## Automation Rules

- Keep the changelog format stable across releases.
- Avoid duplicate entries for the same user-facing change.
- Prefer machine-collected input plus human curation over pure free-text generation.
- If the repo uses PR templates or labels, align the automation to them.
- State the current activation gap explicitly when the repository still relies on manual changelog updates.

## Anti-Patterns

- Dumping raw commits into the changelog
- Mixing internal cleanup with user-facing product changes
- Rewriting release-note categories every release
- Hiding breaking changes inside generic "Changed" entries
