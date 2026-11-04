# Cross-component Business Data Consistency Rules

These rules apply across service and component boundaries. They are the central business-consistency criteria. Apply only when the relevant business flow spans the components or representations described.

## CORE-01 — Data Ownership and Source of Truth

**Objective:** Establish which component owns authoritative business data and which components hold replicas, projections, caches, or derived data.

**Scope / preconditions:** An entity or attribute is read or written by more than one component, or multiple representations exist.

**Checkpoints:**
- Is the authoritative owner identifiable from design and actual write paths?
- Can multiple services independently update the same authoritative fields?
- Are replicas and derived views clearly distinguished from the source of truth?
- Are write permissions and update responsibilities consistent with ownership?

**Failure scenarios:** Conflicting writes; one service treats a stale projection as authoritative; unclear ownership causes updates to be lost.

**Expected behavior:** Each authoritative datum has an identifiable owner and controlled write path. Replicas have defined synchronization semantics.

**Evidence:** Design ownership statements, API contracts, write paths, repositories, event handlers, configuration/access controls.

**Finding criteria:** Report only when evidence shows conflicting ownership, uncontrolled competing writes, or a credible path to lost/conflicting updates. Do not infer ownership from package naming alone.

## CORE-02 — Business Data Definition and Contract

**Objective:** Ensure the same business concept has compatible meaning, identifiers, units, types, nullability, and status semantics across components.

**Scope:** Data crosses service, API, event, database, cache, or file boundaries.

**Checkpoints:**
- Do identifiers refer to the same entity and use compatible formats?
- Are amounts, dates, time zones, units, precision, and rounding semantics consistent?
- Are enum/status values and null/default meanings compatible?
- Are required fields preserved through DTO/entity/event mapping?
- Are schema changes backward/forward compatible for active consumers?

**Failure scenarios:** Currency or unit mismatch; timezone shift; truncation/rounding; incompatible enum; missing field during mapping.

**Expected behavior:** Contracts define semantics, and transformations preserve or intentionally convert them.

**Evidence:** DTOs, schemas, API/event contracts, serializers, mapping code, database definitions, requirements.

**Finding criteria:** A mismatch must be tied to a concrete field or semantic contract. Naming differences alone are not defects.

## CORE-03 — Data Mapping and Transformation

**Objective:** Ensure data transformations preserve business meaning.

**Scope:** Mapping, enrichment, aggregation, serialization, deserialization, or format conversion occurs.

**Checkpoints:**
- Are source and target fields mapped correctly?
- Are optional/default values handled intentionally?
- Are precision, rounding, ordering, and date conversions correct?
- Are derived values calculated from the intended source fields?
- Are unknown or unsupported values handled safely?

**Failure scenarios:** Wrong field mapping; default overwrites valid value; precision loss; stale derived value.

**Expected behavior:** Every transformation has a traceable, semantically correct mapping.

**Evidence:** Mapper classes, conversion utilities, serializers, calculations, contracts, tests.

**Finding criteria:** Report a demonstrated incorrect or lossy transformation, or a credible risk tied to a specific transformation and requirement.

## CORE-04 — Data Completeness Across Boundaries

**Objective:** Prevent required business data from being dropped or only partially propagated.

**Scope:** Data is copied, published, persisted, exported, or represented in another component.

**Checkpoints:**
- Are all required fields propagated?
- Are multi-record/batch operations complete or explicitly partial?
- Can pagination, filtering, limits, or truncation omit records?
- Are partial payloads distinguishable from complete snapshots?
- Are missing fields detected rather than silently defaulted?

**Failure scenarios:** Event omits a required field; batch stops midway; export truncates; a partial update is interpreted as a full snapshot.

**Expected behavior:** Completeness requirements are explicit and partial outcomes are detectable and recoverable.

**Evidence:** Contracts, mapping code, batch loops, pagination, file generation, logs, counts/checksums where available.

**Finding criteria:** Report when required data can be omitted or partial completion is not detected/handled.

## CORE-05 — Data Lifecycle and Deletion Propagation

**Objective:** Keep related representations aligned through create, update, archive, expiry, and delete operations.

**Scope:** An entity has copies or dependent records in multiple components.

**Checkpoints:**
- Are lifecycle events defined?
- Are dependent records, caches, search views, files, and references handled?
- Is soft-delete versus hard-delete semantics consistent?
- Can delayed or failed cleanup leave misleading active data?
- Are retention and legal/business preservation requirements respected?

**Failure scenarios:** Deleted entity remains active in cache; orphan file; dependent record references deleted entity; cleanup removes data still required.

**Expected behavior:** Lifecycle semantics are explicit; propagation/cleanup is reliable, observable, and recoverable.

**Evidence:** Delete/update paths, event handlers, cleanup jobs, TTL/retention config, reference queries, logs.

**Finding criteria:** Do not assume every related record must be deleted. Verify cascade, retention, archival, and soft-delete requirements first.

## CORE-06 — Business State Transition Consistency

**Objective:** Ensure components interpret and transition business states consistently.

**Scope:** A business entity has status/state fields used across components.

**Checkpoints:**
- Are valid transitions defined?
- Can a later state be overwritten by an older event or stale update?
- Do components agree on terminal, retryable, and failure states?
- Are state and associated data updated coherently?
- Are illegal transitions rejected or reconciled?

**Failure scenarios:** Completed entity returns to pending; file is marked ready before it exists; downstream service interprets unknown status incorrectly.

**Expected behavior:** State transitions respect business rules and stale/duplicate transitions do not regress state.

**Evidence:** State enums, transition logic, conditional updates, event handlers, state diagrams, runtime history.

**Finding criteria:** Report only against a documented or clearly implemented state invariant. Do not invent a state machine.

## CORE-07 — Data Synchronization and Propagation

**Objective:** Ensure changes reach all required consumers or replicas under the defined consistency model.

**Scope:** Data is propagated synchronously or asynchronously.

**Checkpoints:**
- Are all required consumers/representations updated?
- Is the synchronization trigger reliable?
- Is there an explicit consistency model and acceptable delay where relevant?
- Can failed propagation be retried or detected?
- Is the source version/timestamp available to detect stale updates?

**Failure scenarios:** Source commits but notification is lost; cache remains stale; one consumer misses an event.

**Expected behavior:** Required propagation is reliable or gaps are detectable and repairable within the business tolerance.

**Evidence:** Update paths, events, listeners, retry mechanisms, outbox/polling jobs, metrics/logs.

**Finding criteria:** A delay is not automatically a defect. Compare observed/design behavior with business freshness requirements.

## CORE-08 — Cross-component Partial Success and Transaction Boundaries

**Objective:** Identify inconsistent intermediate or terminal states when a business operation spans multiple components.

**Scope:** One business operation writes to or invokes more than one independently failing component.

**Checkpoints:**
- What happens if each step succeeds or fails independently?
- Is there a durable record of work to complete?
- Are retries, compensation, or reconciliation defined?
- Can the caller receive success while a required downstream step failed?
- Is the operation's completion state truthful?

**Failure scenarios:** Database commits but event publication fails; metadata commits but file write fails; external call succeeds but local status update fails.

**Expected behavior:** Partial outcomes are detectable and have a defined retry, compensation, or manual recovery path.

**Evidence:** Sequence flow, transaction boundaries, outbox/job tables, retry/compensation code, status updates, logs.

**Finding criteria:** Do not require a distributed transaction. Report an unhandled partial-success path that violates a business invariant or lacks required recovery.

## CORE-09 — End-to-end Idempotency

**Objective:** Prevent retries or repeated requests from causing unintended duplicate business effects.

**Scope:** Operations may be retried, redelivered, resubmitted, or replayed.

**Checkpoints:**
- Is there a stable business/request/event identifier?
- Is duplicate detection scoped correctly?
- Are side effects (writes, files, external calls) protected against duplicate execution?
- Is the idempotency record committed consistently with the business effect?
- Does retry after timeout behave safely?

**Failure scenarios:** Timeout after successful commit leads to duplicate request; replay creates duplicate file or transaction.

**Expected behavior:** Repeated execution produces no unintended additional business effect, or duplicates are explicitly allowed and identified.

**Evidence:** Request keys, unique constraints, deduplication store, conditional updates, retry code, side-effect logic.

**Finding criteria:** Evaluate business semantics. Not every operation must be idempotent, but retryable operations must have safe semantics.

## CORE-10 — Ordering, Concurrency, and Stale Updates

**Objective:** Prevent older or concurrent changes from overwriting newer business state.

**Scope:** Concurrent writers, asynchronous events, parallel jobs, or delayed messages can update the same entity.

**Checkpoints:**
- Does correctness depend on order?
- Is ordering guaranteed at the relevant key/entity boundary?
- Are version, sequence, timestamp, or conditional-write checks used where needed?
- Can stale reads lead to lost updates?
- Are concurrent file/database operations coordinated?

**Failure scenarios:** Older event arrives later and overwrites new value; two read-modify-write operations lose one update.

**Expected behavior:** Ordering/concurrency requirements are explicit and enforced where business correctness depends on them.

**Evidence:** Partition keys, version fields, compare-and-set/conditional updates, locks, transactions, scheduler overlap controls.

**Finding criteria:** Do not require global ordering or locks by default. Demonstrate a conflicting interleaving and its business impact.

## CORE-11 — Failure Recovery and Observability

**Objective:** Ensure failed or incomplete data operations can be detected, diagnosed, and recovered.

**Scope:** A component or integration can fail independently.

**Checkpoints:**
- Are failures observable with correlation/business identifiers?
- Are retries bounded and classified?
- Are permanent failures surfaced for intervention?
- Is recovery safe to repeat?
- Can operators identify pending, stuck, or inconsistent records?

**Failure scenarios:** Silent event loss; endless retry; job marked complete despite failed substep; no way to identify affected entities.

**Expected behavior:** Failure state is visible and recovery is documented, safe, and operationally feasible.

**Evidence:** Exception handling, logs, metrics, alerts, retry/DLQ, status records, runbooks.

**Finding criteria:** Missing logging alone is not automatically a data inconsistency. Connect observability/recovery gaps to a material inability to detect or restore required data.

## CORE-12 — Reconciliation and Integrity Verification

**Objective:** Detect and correct drift between authoritative data and dependent representations.

**Scope:** Asynchronous replication, caches, files, projections, or external systems may diverge.

**Checkpoints:**
- Is reconciliation required by the business risk/tolerance?
- Can expected and actual records be compared?
- Are missing, duplicate, stale, or orphan records detectable?
- Is repair safe, auditable, and repeatable?
- Are reconciliation outcomes recorded?

**Failure scenarios:** Missed event leaves stale projection indefinitely; orphan files accumulate; duplicate records remain undetected.

**Expected behavior:** Where required, drift can be detected and corrected without creating further inconsistency.

**Evidence:** Reconciliation jobs, comparison queries, checksums/counts, repair workflows, audit logs.

**Finding criteria:** Do not demand reconciliation for every integration. Consider criticality, consistency model, and recovery alternatives.

## CORE-13 — Eventual Consistency Contract

**Objective:** Ensure intentional temporary inconsistency has explicit boundaries and converges correctly.

**Scope:** Components are not updated atomically and temporary divergence is possible.

**Checkpoints:**
- Is eventual consistency an intentional design choice?
- Is the maximum acceptable delay defined or inferable from requirements?
- Is convergence guaranteed under retry/recovery assumptions?
- Can consumers distinguish pending/stale from final data?
- What happens if convergence never occurs?

**Failure scenarios:** Stale data persists indefinitely; users interpret pending data as final; retry cannot converge due to poison event.

**Expected behavior:** Temporary divergence is acceptable only within a defined business tolerance and has a reliable convergence/recovery path.

**Evidence:** Requirements, architecture docs, status model, retry/reconciliation mechanisms, timestamps/metrics.

**Finding criteria:** Do not flag short-lived divergence without a violated freshness requirement. If no tolerance is documented, report the requirement gap as `Insufficient Evidence` or a potential design risk, not a confirmed runtime defect.
