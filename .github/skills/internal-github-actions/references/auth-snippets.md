# Cloud Auth Snippets for GitHub Actions

## AWS — OIDC Federation
```yaml
permissions:
  id-token: write
  contents: read

steps:
  - name: Configure AWS credentials
    # aws-actions/configure-aws-credentials@v6.1.0
    # https://github.com/aws-actions/configure-aws-credentials/releases/tag/v6.1.0
    uses: aws-actions/configure-aws-credentials@ec61189d14ec14c8efccab744f656cffd0e33f37
    with:
      role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
      aws-region: eu-south-1
```

Prerequisites:
- IAM OIDC provider for `token.actions.githubusercontent.com`
- IAM role with trust policy scoped to repo/branch
- No long-lived access keys

## Azure — OIDC Federation
```yaml
permissions:
  id-token: write
  contents: read

steps:
  - name: Sign in to Azure
    # Azure/login@v3.0.0
    # https://github.com/Azure/login/releases/tag/v3.0.0
    uses: Azure/login@93381592711f247e165c389ebb30b596c84cdc48
    with:
      client-id: ${{ secrets.AZURE_CLIENT_ID }}
      tenant-id: ${{ secrets.AZURE_TENANT_ID }}
      subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

Prerequisites:
- App registration with federated credential for GitHub Actions
- Service principal with minimal RBAC role
- No client secrets

## GCP — Workload Identity Federation
```yaml
permissions:
  id-token: write
  contents: read

steps:
  - name: Authenticate to Google Cloud
    # google-github-actions/auth@v3.0.0
    # https://github.com/google-github-actions/auth/releases/tag/v3.0.0
    uses: google-github-actions/auth@7c6bc770dae815cd3e89ee6cdf493a5fab2cc093
    with:
      workload_identity_provider: ${{ secrets.GCP_WIF_PROVIDER }}
      service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}
```

Prerequisites:
- Workload Identity Pool with GitHub provider
- Service account with minimal IAM roles
- No service account keys
