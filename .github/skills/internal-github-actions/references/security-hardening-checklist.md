# Workflow Security Hardening Checklist

Use this checklist when a workflow touches deployment, secrets, self-hosted runners, or untrusted contribution paths.

## Event and token boundary

- [ ] Event choice avoids `pull_request_target` for untrusted code.
- [ ] `permissions` are declared explicitly and no job uses `write-all`.
- [ ] `id-token: write` appears only on jobs that actually use OIDC.
- [ ] `workflow_dispatch` inputs are validated before they influence shell or deployment logic.

## Supply chain and execution

- [ ] Third-party actions are pinned to full SHAs with adjacent release comments and URLs.
- [ ] `docker://` references and workflow container images are pinned by digest.
- [ ] Shell steps quote variables and avoid evaluating user-controlled input.
- [ ] Caches and artifacts do not smuggle unreviewed build output into privileged jobs.

## Runner and secret posture

- [ ] Self-hosted runners are restricted to trusted repositories or runner groups.
- [ ] Secrets are scoped to the narrowest job or protected environment that needs them.
- [ ] Forked or untrusted jobs do not gain access to deployment credentials.
- [ ] Production deploys use protected environments with reviewers.

Route organization-wide rulesets, runner governance, and GitHub App policy questions to `.github/skills/internal-github-governance/SKILL.md`.
