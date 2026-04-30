# Terraform Root Structure Standard

## Scope

- This standard applies to repository-owned Terraform or OpenTofu root configurations.
- Reusable modules keep the module layout documented in `../SKILL.md`; they do not use numbered root files.
- Use this as the default for new root configurations unless the target repository or folder already has another credible structure.

## Default root layout

```text
<root>/
  00-init-data.tf
  10-<first-prerequisite-layer>.tf
  20-<next-dependency-branch>.tf
  30-<downstream-domain>.tf
  90-<late-glue-or-observability>.tf
  98-locals.tf
  99-providers.tf
  99-variables.tf
  99-outputs.tf
  terraform.sh
  env/
    <account | subscription | project>/
      backend.ini
      terraform.tfvars
```

## Ordering model

- Numbered files express the intended reading order and logical dependency layers for humans.
- Terraform still resolves execution from the dependency graph, not from file names. If an ordering relationship matters, model it with references, data sources, or explicit `depends_on`.
- `00-*` should contain init-time inputs or fundamental data lookups needed before the rest of the root can be understood or created.
- After `00-*`, assign bands from upstream to downstream: earlier numbers for resources that unblock other layers, later numbers for increasingly dependent branches, late-stage glue, or observability.
- Use tens as coarse grouping lanes for related resource types or responsibility zones, not as a fixed taxonomy that every project must share.
- Leave numeric gaps so new logical layers can be inserted without renaming the whole root.

## Suggested numeric bands

- `00-09`: init, bootstrap wiring, or fundamental data sources required before the rest of the root can make sense.
- `10-97`: dynamic dependency-led bands. Start with the first real prerequisite layer, then keep moving downstream through the root as each layer depends on the previous one.
- Use tens to cluster nearby resource families or responsibility slices while keeping space for inserts such as `11-`, `12-`, or `21-` when a branch needs finer separation.
- Do not treat the middle bands as a fixed universal map such as "20 always means X" or "30 always means Y"; adapt them to the project's dependency tree.
- `98`: locals reserved for derived values.
- `99`: providers, variables, and outputs reserved for the root interface.

## Reserved files

- `98-locals.tf`: derived values only. Do not turn this file into a dump for static configuration that belongs directly in resources or `.tfvars`.
- `99-providers.tf`: `terraform` block, `required_providers`, provider configuration, and any root-level backend declarations that the runner expects.
- `99-variables.tf`: root input interface. Keep variable declarations here instead of scattering them across numbered domain files.
- `99-outputs.tf`: root outputs for downstream consumers, cross-stack references, or operator visibility.
- In new roots, keep these reserved filenames stable even when the numbered domain files change around them.

## Naming guidance

- Use concise domain names after the prefix, such as `00-init-data.tf`, `20-network.tf`, or `40-workloads.tf`.
- Prefer file names that describe responsibility, not CRUD steps or vague buckets like `main.tf` for root configurations.
- Keep tightly coupled resources together in the same numbered file or the same numeric band when they sit at the same dependency layer.
- Split files to preserve readability and logical ownership, not just to maximize the number of files.

## Environment model

```text
env/
  <account | subscription | project>/
    backend.ini
    terraform.tfvars
```

- The `env/<account|subscription|project>/` directory is the default environment selector for repository-owned roots that use `terraform.sh`.
- `backend.ini` contains the backend configuration consumed by `terraform.sh`, typically passed to `terraform init -backend-config=...`.
- `terraform.tfvars` contains the environment-specific input values for that target environment.
- Keep secrets out of committed `terraform.tfvars` files unless the repository already has an approved secret-management pattern for that surface.

## `terraform.sh` contract

- `terraform.sh` should treat the environment name as the selector for both backend and variable inputs.
- The script should resolve `env/<selected-env>/backend.ini` for backend configuration.
- The script should resolve `env/<selected-env>/terraform.tfvars` for plan and apply input values.
- Keep the runner contract explicit so operators can infer the active environment from the folder structure alone.

## Existing layouts and migration

- Do not force this structure onto an existing root that already has a stable, business-meaningful layout.
- When an existing root only partially matches the default, adapt this standard to the local shape instead of damaging the business logic to satisfy naming purity.
- Use this structure as the target shape for migration only when migration is explicitly requested.
- During migration, preserve resource addresses and state intent; if a structural refactor changes addresses, document the required `terraform state mv`, `terraform import`, or other migration steps alongside the change.
