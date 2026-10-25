# Java / Spring Boot Technical Review Method

## 1. Identify the actual stack

Inspect build and configuration files to identify:
- Java version.
- Spring Boot version.
- Maven or Gradle.
- Persistence technology (JPA/Hibernate, JDBC, MyBatis, etc.).
- HTTP client.
- Security framework.
- Messaging and scheduling libraries, if present.
- Test frameworks and existing quality tools.

Do not assume a dependency is used without evidence.

## 2. Correctness and business logic

Check:
- Null handling, optional values, empty collections, and boundary conditions.
- Numeric precision, monetary values, overflow, rounding, and date/time zones.
- State transitions, condition ordering, equality semantics, and collection mutation.
- Exception handling, swallowed exceptions, and incorrect fallback behavior.
- Whether validation runs on the actual execution path.

## 3. Spring transactions

Inspect:
- `@Transactional` placement and actual proxy boundaries.
- Self-invocation and proxy limitations.
- Propagation, isolation, rollback rules, and checked versus unchecked exceptions.
- Transactions combined with HTTP calls or asynchronous work.
- Partial failures and whether side effects can occur outside the transaction.

Do not flag a missing annotation without proving a transaction requirement and a failure scenario.

## 4. Database and persistence

Check:
- N+1 queries and repeated database access.
- Pagination and unbounded result sets.
- Locking, concurrent updates, lost updates, and uniqueness constraints.
- Entity lifecycle and lazy loading when applicable.
- Transaction boundaries and schema migration compatibility.
- Query performance based on actual query paths, not assumptions.

## 5. Concurrency, retries, and idempotency

Check:
- Shared mutable state and race conditions.
- Duplicate requests and duplicate side effects.
- Retry safety, retry limits, and backoff.
- Scheduled task overlap and multi-instance deployment.
- `@Async`, `CompletableFuture`, thread-pool sizing, and exception propagation.
- Lock scope, deadlocks, and resource contention.

Do not recommend distributed locking or idempotency keys indiscriminately. Establish the actual risk.

## 6. HTTP and external integrations

Check:
- Connection/read/request timeouts.
- Connection pool configuration and exhaustion.
- HTTP status and error response handling.
- Retries of non-idempotent operations.
- Partial failure, fallback, and resource cleanup.
- Serialization, date/time formats, precision, and API compatibility.

## 7. Security

Check:
- Authentication and authorization, including object-level authorization.
- Input validation and injection risks.
- SSRF and unsafe deserialization where relevant.
- Sensitive information in logs, errors, responses, or persisted data.
- Secret handling and configuration exposure.

Ground findings in the actual code and applicable threat model.

## 8. Performance and resource management

Check:
- Repeated queries and network calls.
- Unbounded memory use and large result sets.
- Blocking operations and thread starvation.
- Connection, thread, file, stream, and response cleanup.
- Cache behavior and invalidation if changed by the PR.

Explain the conditions under which the issue becomes material.

## 9. Spring wiring and configuration

Check:
- Bean wiring, scope, lifecycle, and conditional configuration.
- `@Profile`, property binding, configuration defaults, and environment overrides.
- Whether annotations and proxies are actually effective.
- API contracts, serialization, validation, and error mapping.
- Startup and deployment compatibility where relevant.

## 10. Tests and operations

Check:
- Unit tests for changed logic and edge cases.
- Integration tests for transactions, persistence, and HTTP contracts.
- Failure and retry scenarios.
- Regression coverage and meaningful assertions.
- Logging, tracing, health checks, and graceful shutdown where relevant.

Do not claim tests passed unless there is execution evidence. Missing tests should be reported separately from confirmed defects.

## Required finding fields

- Finding ID.
- Severity: Critical / High / Medium / Low.
- Category.
- File and line in the PR diff when possible.
- Evidence.
- Concrete failure scenario.
- Technical/business impact.
- Recommended correction.
- Confidence.

Focus on actionable defects introduced by or materially exposed by the PR. Keep potential risks and design suggestions separate from confirmed defects.
