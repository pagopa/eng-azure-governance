---
description: Add or modify entries in structured JSON/YAML registry files
name: cs-data-registry
agent: agent
argument-hint: action=<create|modify|remove> file=<path> key=<identifier> change=<summary>
---

# Data Registry Task

## Required inputs
- **Action**: ${input:action:create,modify,remove}
- **File**: ${input:file}
- **Key**: ${input:key}
- **Change summary**: ${input:change}

## Instructions
1. Use `.github/skills/data-registry/SKILL.md`.
2. Preserve schema and file conventions already used in the repository.
3. Keep modifications minimal and focused on the requested records.
4. Validate cross-file references if the changed record is linked elsewhere.
5. Keep output and documentation in English.

## Minimal example
- Input: `action=modify file=organization/data/members.json key=john.doe change="set active to false"`
- Expected output:
  - Target record updated with no schema break.
  - No duplicate/conflicting entries introduced.
  - Any affected references updated consistently.

## Validation
- Validate JSON/YAML syntax.
- Run project-specific validation checks when available.
- Confirm no duplicate identifiers in the target file.
