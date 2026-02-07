# Code Review Instructions

## Primary checks
1. Security and least privilege.
2. No hardcoded secrets or credentials.
3. Consistency with repository naming and structure conventions.
4. Test coverage for testable logic.
5. Documentation updates when behavior changes.

## Review output format
- `Critical`: must-fix issues
- `Major`: high-risk improvements
- `Minor`: optional improvements
- `Notes`: assumptions and follow-ups

## Focus by area
- Terraform: drift risk, lifecycle safety, variable typing, plan readability.
- Workflows: SHA pinning, minimal permissions, environment protection.
- Scripts: input validation, early returns, readable control flow, English logs.
