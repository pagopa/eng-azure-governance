---
description: Docker and container build standards for secure, reproducible images and pinned digests.
applyTo: "**/Dockerfile,**/Dockerfile.*,**/*.dockerfile,**/.dockerignore,**/docker-compose*.yml,**/docker-compose*.yaml,**/compose*.yml,**/compose*.yaml"
---

# Docker Instructions

## Baseline rules

- Pin base and runtime images by digest and keep a nearby human-readable tag or version reference.
- Prefer multi-stage builds when build tooling is not needed at runtime.
- Run containers as a non-root user unless a documented exception is required.
- Keep `.dockerignore` current so secrets, VCS metadata, caches, and local virtualenvs do not enter the build context.
- Externalize environment-specific configuration and prefer exec-form `CMD` or `ENTRYPOINT`.
- Avoid privileged mode, host networking, and broad bind mounts unless explicitly justified.

## Use the skill for deeper guidance

- Load `.github/skills/internal-docker/SKILL.md` for Dockerfile patterns, Compose topology choices, common mistakes, and container-hardening detail.
- Keep this instruction as the auto-loaded baseline; keep workflow depth and examples in the skill.

## Validation

- Validate Dockerfile or Compose syntax when tooling is available.
- Check that image references remain digest-pinned before merge.
- Review the final runtime stage for unnecessary tooling, shells, or package managers.
