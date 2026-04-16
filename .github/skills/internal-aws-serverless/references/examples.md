# AWS Serverless Examples

## HTTP Lambda shape

Use this pattern when Lambda is the transport adapter for an HTTP endpoint:

- Parse body, path parameters, and query parameters once.
- Validate required fields before calling business logic.
- Return one normalized response shape for success and error cases.
- Keep the response mapper small and explicit.

```javascript
export async function handler(event, context) {
  const requestId = context.awsRequestId;
  const id = event.pathParameters?.id;

  if (!id) {
    return json(400, { error: "Missing id" });
  }

  try {
    const item = await getItem({ id, requestId });
    return json(200, item);
  } catch (error) {
    console.error("get-item-failed", { requestId, message: error.message });
    return json(error.statusCode ?? 500, { error: "Internal server error" });
  }
}

function json(statusCode, payload) {
  return {
    statusCode,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  };
}
```

Node.js note:

- Set `context.callbackWaitsForEmptyEventLoop = false` only when open handles are intentional and understood.

## SQS batch consumer shape

Use this pattern when one bad message must not fail the whole batch:

```python
import json
import logging

logger = logging.getLogger(__name__)


def handler(event, context):
    failures = []

    for record in event["Records"]:
        try:
            message = json.loads(record["body"])
            process_message(message)
        except Exception as exc:
            logger.error(
                "process-message-failed",
                extra={"message_id": record["messageId"], "error": str(exc)},
            )
            failures.append({"itemIdentifier": record["messageId"]})

    return {"batchItemFailures": failures}
```

Queue checklist:

- Enable partial batch failure reporting when the event source supports it.
- Keep the queue visibility timeout comfortably above the Lambda timeout.
- Attach a DLQ or another explicit failure path.
- Make `process_message` idempotent.

## Scheduled Lambda shape

Use this pattern when the function runs from EventBridge or another scheduler:

- Accept that schedules can arrive late, retry, or overlap.
- Make the target time window explicit in logs and downstream calls.
- Protect side effects with idempotent markers or a coordination lock when overlap would be harmful.

## Packaging checklist

- Keep one function package focused on one responsibility.
- Prefer modular SDK clients over broad imports.
- Measure init duration before assuming the bottleneck is invocation logic.
- If multiple functions share the same large dependency, consider a versioned layer only after confirming the tradeoff is worth it.
