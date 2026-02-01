# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability in this repository, please report it responsibly:

1. **Do NOT** create a public GitHub issue
2. Contact the Cloud Engineering team directly
3. Provide details about the vulnerability
4. Allow time for the issue to be addressed

## Best Practices

### Credentials

- Never commit credentials, tokens, or secrets
- Use Azure Key Vault for sensitive data
- Rotate credentials regularly

### Azure Policies

- Test policies in non-production first
- Consider impact before using Deny effect
- Document exemptions and their justification
- Review policies regularly

### Custom RBAC Roles

- Follow least privilege principle
- Avoid wildcards in permissions
- Document why each permission is needed
- Review roles periodically

### Terraform State

- State files contain sensitive information
- State is stored in Azure Storage Account
- Access to state is restricted

## Security Checks

The CI pipeline includes:

- Terraform validation
- Drift detection
- Pre-commit hooks for common issues
- Code review requirements
