# Decision Guide: Feature (Inline) vs Module

## Quick decision rule

> If the same resource group is used by **2 or more** root configurations or repositories, extract it into a module. Otherwise, keep it inline.

## Decision flowchart

```
Is this resource group reused across 2+ root configs or repos?
├── YES → Create a module
│         ├── Define interface (variables.tf + outputs.tf)
│         ├── Pin provider versions in versions.tf
│         ├── Add README with usage example
│         └── Publish to registry or local path
└── NO → Keep inline (feature)
         ├── Will it likely be reused soon?
         │   ├── YES → Keep inline now, mark with a TODO for extraction
         │   └── NO → Keep inline permanently
         └── Is it a complex resource group with its own lifecycle?
             ├── YES → Consider a module even without reuse (isolation benefit)
             └── NO → Inline is the right choice
```

## Signals that inline is correct
- Single environment or single root config only
- Simple resource (S3 bucket, IAM role, security group)
- No consumers outside the current project
- The resource lifecycle is tightly coupled to its parent

## Signals that a module is correct
- Same pattern appears in multiple environments with small parameter changes
- The resource group has 5+ resources working together
- Multiple teams or repositories need the same infrastructure pattern
- The group has its own lifecycle (can be created/destroyed independently)
- You need to enforce a standard interface across projects

## Anti-patterns
- **Premature module**: Creating a module "just in case" with only one consumer → adds indirection without benefit
- **God module**: A single module that provisions 20+ resources for an entire application → loses composability
- **Leaky module**: Module exposes internal resource attributes instead of stable output contracts → consumers break on internal refactors
