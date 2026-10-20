# Azure Policy: Kubernetes

This Terraform root defines custom Azure Policy controls for Azure Kubernetes Service.

## Purpose

Use this directory for Kubernetes policy controls covering allowed cluster versions and SKUs, Defender profile, image SHA-256 references, the required policy add-on, and required PodDisruptionBudget coverage. The root resolves the `pagopa` management group and exposes the policy IDs shown in the generated Terraform reference below.

## Layout

- `00_data.tf` resolves the management group.
- `01_*.tf` defines the Kubernetes policies.
- `99_providers.tf` configures Terraform, the provider, and the partial backend.
- `99_variables.tf` and `99_outputs.tf` declare the root interface.
- `env/org/` contains the subscription selection, backend settings, and inputs.
- `policy_rules/` contains policy parameters, rules, and Gatekeeper templates.
- `tests/` contains native Terraform tests.
- `terraform.sh` links to the shared repository runner.

## Usage

From this directory, use the shared runner with the `org` environment:

```bash
./terraform.sh init org
./terraform.sh plan org
```

Review the plan before running `./terraform.sh apply org`. The backend settings
in `env/org/backend.tfvars` retain the existing storage account, container, and
state key. This layout change requires no resource moves or state migration.
The former `./terraform.sh <action>` invocation now requires `org`.

## Validation

From this directory, run non-remote Terraform validation:

```bash
terraform fmt -check .
terraform init -backend=false -lockfile=readonly
terraform validate -no-color
terraform test -filter=tests/required_pdb.tftest.hcl -no-color
```

Native tests require Terraform 1.7 or later and use a mocked Azure provider.
They do not access Azure or create real resources.

## Offline policy tests

The Gatekeeper suite for the required PDB rule runs without a cluster. Use gator 3.23.1, the version pinned in the repository-root `.gator-version`. Install it with `brew install gator`, confirm the version, then run from this directory:

```bash
gator verify policy_rules/tests/required_pdb/
```

The suite has 26 cases for Deployments and StatefulSets. It covers the `minReplicas` threshold and the PDB selector rules. Gator cannot set `review.namespace`, so the fallback from `metadata.namespace` to `review.namespace` is not tested offline. Live behavior still needs the human checks in the [rollout runbook](../03_policy_set/README.md#rollout-runbook).

## Required PodDisruptionBudget control

The custom definition `kubernetes_required_pdb` reports Deployments and StatefulSets whose `spec.replicas` is at least `minReplicas` (default 3) and that have no covering PodDisruptionBudget. In PROD it runs beside the Azure built-in PDB definition. It does not replace that definition.

A PodDisruptionBudget covers a workload only when all of these conditions hold:

- `spec.selector.matchLabels` is not empty.
- The `matchExpressions` field is absent. An empty list does not count.
- Every `matchLabels` key and value equals a label in the workload pod template.

Workload labels alone do not establish coverage. PDBs with `matchExpressions`, mixed selectors, or empty selectors do not cover a workload. This limit is intentional. Do not add generic selector support without a new review.

Parameters: `effect` (`Audit` by default, `Deny`, or `Disabled`), `minReplicas` (default 3), `namespaces`, `excludedNamespaces`, and `labelSelector`.

Limits:

- Azure Policy syncs Deployments, StatefulSets, and PodDisruptionBudgets into Gatekeeper. This sync raises Gatekeeper memory use.
- The custom rule depends on that synced inventory. It does not install its own sync. Live behavior depends on the built-in preview, which may change.
- Each policy reports at most 500 non-compliant records per cluster. A workload missing from a truncated report does not prove compliance.
- Compliance can lag by up to 15 minutes. Treat older results as stale.
- HPA and KEDA change `spec.replicas` at runtime, so compliance can change over time. Do not use the replica count from the manifest.
- Namespaces in `excludedNamespaces` are skipped. New references in those namespaces are not checked.

Rollback: set the `required_pdb` effect to `Disabled` in the PROD policy set in [01_kubernetes_prod.tf](../03_policy_set/01_kubernetes_prod.tf), then apply that root. This change does not affect the built-in PDB reference.

No diagram is provided because this directory is a single policy root and the generated reference below enumerates its definitions, inputs, and outputs precisely.

<!-- markdownlint-disable -->
<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.3.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | ~> 4.63.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | 4.63.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_policy_definition.kubernetes_allowed_kubernetes_version](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.kubernetes_allowed_sku](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.kubernetes_required_defender_profile](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.kubernetes_required_image_sha256](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.kubernetes_required_pdb](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.kubernetes_required_policy_addon](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/management_group) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_subscription_id"></a> [subscription\_id](#input\_subscription\_id) | The Azure subscription ID to use | `string` | n/a | yes |
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_kubernetes_allowed_kubernetes_version_id"></a> [kubernetes\_allowed\_kubernetes\_version\_id](#output\_kubernetes\_allowed\_kubernetes\_version\_id) | n/a |
| <a name="output_kubernetes_allowed_sku_id"></a> [kubernetes\_allowed\_sku\_id](#output\_kubernetes\_allowed\_sku\_id) | n/a |
| <a name="output_kubernetes_required_defender_profile_id"></a> [kubernetes\_required\_defender\_profile\_id](#output\_kubernetes\_required\_defender\_profile\_id) | n/a |
| <a name="output_kubernetes_required_image_sha256_id"></a> [kubernetes\_required\_image\_sha256\_id](#output\_kubernetes\_required\_image\_sha256\_id) | n/a |
| <a name="output_kubernetes_required_policy_addon_id"></a> [kubernetes\_required\_policy\_addon\_id](#output\_kubernetes\_required\_policy\_addon\_id) | n/a |
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
<!-- END_TF_DOCS -->
