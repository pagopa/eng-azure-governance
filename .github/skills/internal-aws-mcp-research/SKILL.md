---
name: internal-aws-mcp-research
description: Use when the task needs current AWS documentation or safe IAM inspection for Organizations, SCPs, IAM policies, delegated administrators, regional availability, or StackSets, and the assistant should prefer AWS Knowledge MCP and AWS IAM MCP when available.
---

# Internal AWS MCP Research

Use this skill when AWS decisions depend on up-to-date documentation or on safe inspection of real IAM state.

## When to use

- The task needs current AWS documentation, regional availability facts, or official AWS guidance that may have changed.
- The task needs safe IAM inspection or policy simulation for Organizations, SCPs, IAM policies, roles, or delegated administrators.
- AWS Knowledge MCP or AWS IAM MCP should be preferred when available, with an AWS-doc fallback when they are not.

## Purpose

This skill standardizes an AWS research workflow that prefers AWS MCP servers when available and falls back to official AWS documentation when they are not.

It is designed for principal-level platform governance questions, not only for application coding.

## Source priority

1. AWS Knowledge MCP for current AWS documentation, latest guidance, and regional availability
2. AWS IAM MCP in read-only mode for account-specific IAM inspection and policy simulation
3. Official AWS documentation when MCP is unavailable or insufficient

Do not assume both MCP servers are configured in the current client or session.

## Server expectations

Common server identities:

- AWS Knowledge MCP: `aws-knowledge-mcp-server`
- AWS IAM MCP: `awslabs.iam-mcp-server` or `iam-mcp-server`

The exact configured name can vary by client.

## Research workflow

1. Classify the question.
   - Documentation, best practices, service behavior, regional support: start with AWS Knowledge MCP
   - Real IAM state, principals, attached policies, or permission testing: use AWS IAM MCP
   - Mixed questions: use Knowledge MCP first, then IAM MCP for confirmation
2. Detect available AWS MCP servers in the current environment.
3. Use the safest tool path first.
   - Knowledge MCP for documentation lookup
   - IAM MCP in read-only mode for inspection and `simulate_principal_policy`
4. If AWS MCP is unavailable, use official AWS documentation from `references/official-source-map.md`.
5. Summarize the answer with source type clearly labeled:
   - AWS docs or Knowledge MCP guidance
   - live IAM observation
   - inferred recommendation

## AWS Knowledge MCP usage

Use AWS Knowledge MCP for:

- service documentation and API behavior
- best practices and architectural guidance
- latest public AWS guidance
- regional availability checks
- CloudFormation and CDK reference lookups

Prefer these tool patterns when available:

- `search_documentation` to find relevant pages
- `read_documentation` to pull the exact page into markdown
- `recommend` to expand from one AWS page to adjacent guidance
- `list_regions` and `get_regional_availability` for region-sensitive design

## AWS IAM MCP usage

Default to read-only and simulation-oriented work.

Use AWS IAM MCP for:

- listing users, roles, groups, and policies
- retrieving attached or inline policy details
- understanding trust relationships
- testing policy effects with `simulate_principal_policy`

Prefer these operations when available:

- `list_users`
- `get_user`
- `list_roles`
- `list_groups`
- `get_group`
- `list_policies`
- `get_user_policy`
- `get_role_policy`
- `list_user_policies`
- `list_role_policies`
- `simulate_principal_policy`

## Safety rules

- Treat IAM MCP as read-only by default.
- Do not create, delete, attach, detach, or rotate IAM resources unless the user explicitly asks for a change and the blast radius is understood.
- Prefer `simulate_principal_policy` before proposing policy rollout steps.
- Distinguish clearly between documentation-backed statements and observations from a real AWS account.
- When the answer affects strategic framing, route the recommendation back through `internal-aws-strategic`.
- When the answer affects account layout, delegated admin placement, or StackSets topology, route it through `internal-aws-organization-structure`.
- When the answer affects SCPs, IAM, trust, or federation, route it through `internal-aws-governance`.
- When the answer affects validation, backup, monitoring, or rollout evidence, route it through `internal-aws-operations`.

## Output expectations

- Research question and scope
- MCP availability used or missing
- Sources consulted
- What is confirmed by AWS docs or MCP
- What remains an architectural recommendation or inference
- Safe next steps

## References

- `references/official-source-map.md`
- `references/mcp-capabilities.md`
- `../internal-aws-strategic/SKILL.md`
- `../internal-aws-organization-structure/SKILL.md`
- `../internal-aws-governance/SKILL.md`
- `../internal-aws-operations/SKILL.md`
