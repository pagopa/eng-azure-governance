# AWS MCP Capabilities

Use this reference to choose the safest AWS MCP path for the question at hand.

## AWS Knowledge MCP

Best for:

- current AWS documentation
- architecture and best-practice lookups
- regional availability checks
- CloudFormation and CDK reference discovery

Notable capabilities from the server documentation:

- `search_documentation`
- `read_documentation`
- `recommend`
- `list_regions`
- `get_regional_availability`

Operational notes:

- remote HTTP server
- public internet access required
- no AWS account or AWS authentication required
- subject to rate limits

## AWS IAM MCP

Best for:

- inspecting current IAM state in an AWS account
- listing users, roles, groups, and policies
- retrieving inline policy details
- simulating permissions before rollout

Operational notes:

- requires AWS credentials
- supports read-only mode and should default to it for analysis
- mutating operations exist, so treat them as explicit-change tools, not as default exploration tools

## Recommended split of responsibilities

| Question type | Preferred server |
|---|---|
| "What does AWS currently recommend?" | AWS Knowledge MCP |
| "Which regions support this?" | AWS Knowledge MCP |
| "What does this role or user currently have?" | AWS IAM MCP |
| "Would this policy allow action X on resource Y?" | AWS IAM MCP with simulation |
| "How should we govern this across the org?" | `internal-aws-strategic` first, then `internal-aws-organization-structure` or `internal-aws-governance` plus whichever MCP source supplies the facts |
