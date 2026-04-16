---
name: internal-aws-serverless
description: Use when the user needs to design, implement, refactor, or review AWS Lambda and adjacent serverless code such as API Gateway-backed handlers, SQS-triggered processors, event-source-specific retry behavior, package-size or cold-start tradeoffs, and AWS-specific runtime configuration after the broader AWS platform decision is already made.
---

# Internal AWS Serverless

Follow `.github/instructions/internal-lambda.instructions.md` for the baseline Lambda rules. This skill adds AWS-specific implementation guidance only.

## When to use

- Implementing or reviewing AWS Lambda handlers in Python, Node.js, or TypeScript.
- Designing API Gateway, Lambda Function URL, or other HTTP-triggered request and response handling.
- Designing SQS-triggered batch processing, retry behavior, DLQ handling, or partial batch failure flows.
- Making packaging, dependency, cold-start, VPC, or runtime-configuration choices that are specific to AWS Lambda behavior.

## When not to use

- The main problem is still strategic AWS decision support rather than implementation.
- The main problem is IAM, SCP, trust, or organization-structure design.
- The next need is operational evidence, rollout validation, monitoring posture, or DR validation rather than handler design.
- The task is generic Python or Node.js module design with no AWS serverless behavior in scope.

## Core guidance

- Keep the Lambda handler as a transport adapter; move business logic to testable helpers or services.
- Make the event source explicit and code to one contract at a time: HTTP, queue, schedule, or another async trigger.
- Parse and validate inputs at the boundary, then normalize the data passed to business logic.
- Initialize AWS clients outside the handler when reuse is safe, but keep imports and dependencies small.
- Prefer modular AWS SDK clients and narrow dependencies over broad convenience packages.
- Size timeout, memory, concurrency, batch size, and queue visibility timeout as one operating profile instead of independent toggles.
- Treat duplicate delivery, retries, and idempotency as normal behavior for asynchronous triggers.
- Use environment variables for configuration only; fetch secrets from managed secret stores.
- Log stable identifiers such as request IDs and message IDs, but do not log raw sensitive payloads by default.

## Event-source guidance

- **HTTP**: Normalize body, path, and query parsing once; return transport-compatible JSON responses with explicit headers; keep CORS intentional.
- **SQS**: Process records independently, handle poison messages explicitly, and return only failed item identifiers when partial batch retry is enabled.
- **Scheduled events**: Make time-window assumptions explicit and guard against duplicate or overlapping execution.
- **File-driven workflows**: Avoid recursive triggers by separating input and output prefixes or buckets.

Load `references/examples.md` when you need minimal AWS-specific handler patterns or event-source checklists.

Load `references/sharp-edges.md` when diagnosing cold starts, VPC latency, retry storms, response-shape mismatches, or file-ingest recursion.

## Relationship to adjacent skills

- `internal-aws-strategic`
  Use when the AWS direction or tradeoff is still unsettled.
- `internal-aws-governance`
  Use when the next question is IAM, trust, queue policy, or another guardrail design concern.
- `internal-aws-operations`
  Use when the next question is rollout validation, monitoring, evidence, or recovery proof rather than implementation.
- `internal-project-python`
  Use alongside this skill when the Lambda code lives in structured Python application modules.
- `internal-project-nodejs`
  Use alongside this skill when the Lambda code lives in structured Node.js or TypeScript modules.
- `internal-terraform`
  Use when the primary change is Terraform infrastructure rather than runtime code.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Treating the handler as the business layer | Hard to test, high coupling to AWS events | Keep the handler thin and call testable helpers |
| Parsing every event inline differently | Inconsistent behavior and brittle error handling | Normalize one event contract per trigger type |
| Returning whole-batch failure for one bad SQS record | Causes replay storms and blocks healthy messages | Catch per-record failures and return failed IDs only when supported |
| Ignoring idempotency on async triggers | Duplicate deliveries create data corruption or repeated side effects | Use idempotent writes, dedupe keys, or safe upserts |
| Shipping large shared bundles to every function | Slower cold starts and harder ownership boundaries | Split by function responsibility and keep dependencies narrow |
| Putting secrets directly in environment variables | Rotation and exposure risks | Use Secrets Manager or SSM-backed retrieval patterns |
| Attaching Lambda to a VPC by default | Adds latency and networking failure modes | Keep it out of a VPC unless there is a concrete dependency |
| Mixing HTTP response shaping with core logic | Hard to reuse and easy to break integrations | Keep request mapping and response mapping at the edge |

## Validation

- Run unit tests outside the Lambda runtime and mock AWS boundaries.
- For HTTP handlers, test malformed body, path, query, and error-response cases.
- For queue consumers, test duplicate delivery, poison messages, timeout pressure, and partial batch failure behavior.
- Validate code assumptions together with the deployed timeout, memory, event-source, and queue configuration.
