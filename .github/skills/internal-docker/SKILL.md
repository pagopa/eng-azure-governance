---
name: internal-docker
description: Use when creating or modifying Dockerfiles, Compose assets, image build settings, or container hardening rules.
---

# Docker Skill

## When to use

- Creating or updating `Dockerfile` assets.
- Editing Compose manifests or workflow-local image references.
- Hardening container build and runtime configuration.

## Mandatory rules

- Pin images by digest (`@sha256:...`), never by floating tag alone.
- Use multi-stage builds to separate build and runtime layers.
- Run as non-root user in the final stage.
- Use `COPY --from=build` to bring only compiled artifacts into runtime.
- Minimize layer count — combine related `RUN` commands.
- Always include a `.dockerignore` to exclude `.git`, `node_modules`, `__pycache__`, etc.

## Dockerfile patterns

Load `references/dockerfile-patterns.md` when you need the canonical multi-stage or single-stage example.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Using `latest` or floating tags | Non-reproducible builds, supply-chain risk | Pin by digest: `image@sha256:abc...` |
| Running as root in production | Container escape gives host-level privileges | Add `USER node` / `USER nobody` in final stage |
| Copying entire context without `.dockerignore` | Bloated image with `.git`, secrets, dev deps | Create `.dockerignore` excluding non-essential files |
| Installing dev dependencies in runtime stage | Larger image, unnecessary attack surface | Use multi-stage: install in build, copy only artifacts |
| One `RUN` per command | Excessive layers, larger image, slower pulls | Combine related commands with `&&` |
| Missing `--no-cache-dir` on pip install | Wasted space from pip cache in layer | Always `pip install --no-cache-dir` |

## Validation

- Verify image references use digests.
- Verify non-root user in final stage.
- Verify `.dockerignore` exists and excludes sensitive/unnecessary files.
- Build or lint the container definition when tooling is available.
