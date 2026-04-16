# Official Source Map

Use this file as a starting map, not as a substitute for opening the live docs.

## Core GitHub Copilot customization docs

- `https://docs.github.com/en/copilot/concepts/prompting/response-customization`
  - Use for the customization model: repository-wide instructions, path-specific instructions, agent instructions, and when to avoid overloading repository-wide guidance.
- `https://docs.github.com/en/copilot/how-tos/configure-custom-instructions`
  - Use for the high-level entry point to personal, repository, and organization custom instructions.
- `https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions?tool=vscode`
  - Use for repository custom instructions and environment-specific behavior.

## Custom agents and skills

- `https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents`
  - Use for what custom agents are, where they are supported, and the high-level model that custom agents can specify tools and MCP servers.
- `https://docs.github.com/en/copilot/reference/custom-agents-configuration`
  - Use as the primary source for supported frontmatter fields, current tool aliases, MCP tool namespacing, retired `infer`, and environment-specific behavior.
- `https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents`
  - Use for custom agent structure, authoring workflow, and current GitHub-managed examples.
- `https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-skills`
  - Use for agent skills and for the skill-versus-custom-instructions boundary.
- `https://docs.github.com/en/copilot/tutorials/customization-library/custom-agents/your-first-custom-agent`
  - Use for GitHub-maintained example patterns after the schema and tool rules have been verified in the reference docs.

## MCP

- `https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers`
  - Use for MCP server setup, built-in GitHub MCP behavior in Copilot CLI, and server configuration patterns.
- `https://docs.github.com/en/copilot/concepts/prompting/response-customization`
  - Also use for the relationship between repository customization and MCP-aware Copilot surfaces.

## VS Code Copilot customization docs

- `https://code.visualstudio.com/docs/copilot/customization/custom-agents`
  - Use for VS Code custom agent file structure, frontmatter fields (`agents`, `handoffs`, `hooks`, `user-invocable`, `disable-model-invocation`), tool list priority, and agent sharing.
- `https://code.visualstudio.com/docs/copilot/agents/subagents`
  - Use for subagent invocation, coordinator/worker orchestration patterns, nested subagents, and `agents:` restriction.
- `https://code.visualstudio.com/docs/copilot/copilot-customization`
  - Use for the VS Code customization overview: instructions, agents, and skills.
- `https://code.visualstudio.com/docs/copilot/chat/chat-agent-mode`
  - Use for agent mode behavior, tool usage, and session-level agent configuration in VS Code.
- `https://code.visualstudio.com/docs/copilot/customization/agent-skills`
  - Use for VS Code agent skills structure and skill-versus-instruction boundary.

## Task-quality guidance

- `https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results`
  - Use for scoping, task clarity, and choosing the right Copilot mechanism for a given job.
