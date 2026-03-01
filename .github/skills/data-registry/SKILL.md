---
name: data-registry
description: Safely update structured JSON/YAML registry files (users, groups, teams, repositories, or policy maps).
---

# Data Registry Skill

## When to use
- Add or update records in structured JSON/YAML data files.
- Apply naming/order conventions across registry-like data.
- Validate referential integrity between related data files.

## Mandatory rules
- Preserve existing schema and file format.
- Keep keys ordered when repository convention requires it.
- Avoid duplicate identifiers and conflicting records.
- Keep comments/documentation in English.

## Common checks
- Unique IDs, names, usernames, emails, and slugs.
- Cross-file references point to existing entries.
- Required fields are present for each object.
- Sort order follows repository conventions.

## Minimal example
```json
{
  "id": "example-user",
  "email": "example@company.com",
  "role": "read"
}
```

## Validation
- Run repository checks for JSON/YAML syntax.
- Run domain-specific validation scripts when available.
- Keep changes minimal and scoped to requested records.
