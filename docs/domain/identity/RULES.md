# Identity Rules

These rules govern the repository's production workload identity and its Azure access grants.

## IDN-001 - Authenticate through federation

- Rule ID: IDN-001
- Serves: PRI-02
- Owner: Identity
- Severity: blocking
- Enforcement owner: not enforced
- Evidence: `.identity/02_identity_prod.tf`
- Remediation: Replace any static secret with the repository's federated identity credential for the target GitHub environment.
- Rule: The production identity is trusted only through federated, short-lived credentials bound to a repository environment; it never relies on a client secret.

## IDN-002 - Bound every identity grant

- Rule ID: IDN-002
- Serves: PRI-01
- Owner: Identity
- Severity: blocking
- Enforcement owner: not enforced
- Evidence: `.identity/02_identity_prod_auth.tf`, `SECURITY.md`
- Remediation: Replace a broad role or scope with the narrowest role and scope that provide the needed operational capability, or record an evidence-backed exception.
- Rule: Each identity grant gives the production identity one bounded operational capability at the narrowest effective scope.
