# AWS Serverless Sharp Edges

| Sharp edge | Why it happens | Check first | Typical mitigation |
|---|---|---|---|
| Cold starts feel randomly slow | Large bundles, heavy imports, or VPC setup dominate init time | Init duration, package size, import graph, VPC attachment | Reduce dependencies, split functions, profile init work, remove unnecessary VPC use |
| Lambda in a VPC times out on external calls | DNS, route, NAT, or security configuration is incomplete | Whether the function really needs a VPC, subnet routes, DNS, egress path | Keep Lambda out of a VPC unless required; otherwise validate DNS and egress explicitly |
| SQS retry storms | One record failure causes whole-batch replay | Batch size, handler error path, partial batch failure support | Catch per-record exceptions and return failed IDs only |
| Messages never reach the DLQ when expected | Visibility timeout or retry assumptions are wrong | Queue redrive policy, Lambda timeout, visibility timeout, max receives | Size queue and function settings together and test the failure path |
| API Gateway returns 502 or malformed responses | Response shape does not match the configured integration | Integration type, headers, JSON body serialization, status code mapping | Centralize the HTTP response mapper and test failure cases |
| Large uploads or downloads break through Lambda | Payload, memory, timeout, or `/tmp` constraints are exceeded | Object size, API limits, temp-storage needs, transfer path | Use presigned S3 flows, stream when possible, keep Lambda out of bulk transfer paths |
| File workflows recurse forever | Input and output use the same trigger surface | Bucket notification scope, prefixes, output location | Separate input and output prefixes or buckets |
| Node.js invocations hang after work is done | Open sockets, timers, or connection pools keep the event loop alive | Client lifecycle, timers, runtime settings | Close unused handles or intentionally set `callbackWaitsForEmptyEventLoop = false` |
| Secrets leak into logs or configs | Secrets are treated like normal configuration values | Environment variables, startup logs, error serialization | Use managed secret stores and scrub logs by default |
