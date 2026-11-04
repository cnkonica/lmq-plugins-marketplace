# Kafka Data Consistency Rules

Apply only to Kafka paths in the scoped business flow. Kafka delivery guarantees do not automatically guarantee end-to-end business consistency across a database and external side effects.

## KFK-01 — Event Contract and Identity

**Objective:** Ensure producer and consumer agree on event meaning, schema, identity, and version.
**Scope:** Business events are published and consumed.
**Checkpoints:** Event ID, aggregate/business ID, event type, schema/version, required fields, timestamp semantics, compatibility.
**Failure scenarios:** Consumer interprets field/status differently; event cannot be correlated to entity.
**Expected behavior:** Event contract is explicit and compatible.
**Evidence:** Event classes/schemas, serializers, producer/consumer code, contract docs.
**Finding criteria:** Identify concrete semantic or compatibility mismatch.

## KFK-02 — Event Completeness and Semantics

**Objective:** Ensure event payload contains sufficient and correct information for its intended consumers.
**Scope:** Consumer uses event payload to update business data.
**Checkpoints:** Snapshot versus delta semantics; required fields; null/absent distinction; event meaning; source version.
**Failure scenarios:** Consumer treats delta as full snapshot; omitted field resets target.
**Expected behavior:** Payload semantics are explicit and consumer interpretation matches.
**Evidence:** Producer mapping, consumer handler, schema, requirements.
**Finding criteria:** Do not require all events to carry full entity snapshots.

## KFK-03 — Publication Reliability

**Objective:** Prevent a committed business change from silently losing its required event.
**Scope:** A database change and Kafka publication represent one logical business operation.
**Checkpoints:** Ordering of DB commit and publish; outbox/CDC/polling alternative; send result handling; retry; crash window.
**Failure scenarios:** DB commit succeeds, process crashes before publish.
**Expected behavior:** Required event publication is durable or missing publication is detectable/recoverable.
**Evidence:** Transaction code, producer callbacks, outbox/CDC, retry and recovery jobs.
**Finding criteria:** Do not require outbox universally; establish whether lost event violates the business contract.

## KFK-04 — Duplicate Message Processing

**Objective:** Prevent redelivery/replay from creating duplicate business effects.
**Scope:** Consumer operations may be redelivered or replayed.
**Checkpoints:** Stable event ID; deduplication; idempotent writes; external side effects; dedup record/business update atomicity.
**Failure scenarios:** Consumer writes DB then crashes before offset commit; message is redelivered.
**Expected behavior:** Duplicate delivery does not create unintended duplicate effects.
**Evidence:** Consumer handler, DB update, dedup store, offset config, external calls.
**Finding criteria:** Delivery may be at-least-once; assess business handler semantics rather than assuming duplicates never occur.

## KFK-05 — Ordering and Stale Events

**Objective:** Preserve business ordering where event order affects state.
**Scope:** Multiple events for same entity may be processed asynchronously.
**Checkpoints:** Partition key; ordering scope; concurrent consumers; event sequence/version; stale-event rejection.
**Failure scenarios:** Older update arrives after newer update and regresses state.
**Expected behavior:** Required per-entity order is preserved or stale events are detected.
**Evidence:** Producer key, topic/partition config, consumer concurrency, version checks, state logic.
**Finding criteria:** Do not require global topic ordering.

## KFK-06 — Offset and Business Processing Boundary

**Objective:** Ensure offset commits do not cause loss of required business processing.
**Scope:** Consumer manually or automatically commits offsets.
**Checkpoints:** Commit timing; auto-commit; processing success definition; batch partial failure; rebalance behavior.
**Failure scenarios:** Offset committed before durable business effect; partial batch acknowledged as complete.
**Expected behavior:** Offset progression reflects the required processing guarantee.
**Evidence:** Consumer config, poll/commit code, error handling, batch logic.
**Finding criteria:** Evaluate actual framework/container semantics; do not infer behavior from absence of explicit commit call.

## KFK-07 — Retry and Poison Message Handling

**Objective:** Ensure failed messages are retried or isolated without silent loss or uncontrolled duplication.
**Scope:** Consumer can fail to process messages.
**Checkpoints:** Retryable versus permanent errors; retry limits/backoff; blocking behavior; DLQ routing; replay procedure; ordering effects.
**Failure scenarios:** Message skipped after retry exhaustion; poison message blocks required stream; replay duplicates side effects.
**Expected behavior:** Failure is visible and recoverable under the business contract.
**Evidence:** Error handlers, retry topics, DLQ config, alerts, runbooks.
**Finding criteria:** A DLQ is not mandatory in every architecture; verify safe handling and visibility.

## KFK-08 — Dead-letter and Recovery Completeness

**Objective:** Ensure diverted messages remain traceable and can be safely resolved.
**Scope:** DLQ or equivalent failure isolation exists or is required.
**Checkpoints:** Original event identity preserved; reason/context retained; ownership/alerting; replay safety; reconciliation after repair.
**Failure scenarios:** DLQ messages are never reviewed; replay creates duplicate or stale state.
**Expected behavior:** Failed events remain actionable and replay/repair preserves business invariants.
**Evidence:** DLQ producer/consumer, metadata, dashboards, replay tooling, runbooks.
**Finding criteria:** Report operational gaps when they make required business data unrecoverable or unobservable.

## KFK-09 — Event Schema Evolution

**Objective:** Preserve compatibility during producer/consumer version changes.
**Scope:** Event schemas evolve or services deploy independently.
**Checkpoints:** Add/remove/rename/type changes; default values; enum expansion; consumer tolerance; topic retention and old messages.
**Failure scenarios:** New producer breaks old consumer; replayed old event cannot be parsed.
**Expected behavior:** Evolution policy matches deployment and replay requirements.
**Evidence:** Schema registry/config, event models, version handling, deployment process.
**Finding criteria:** A version field is not mandatory if compatibility is otherwise safely maintained.

## KFK-10 — Replay and Reprocessing

**Objective:** Ensure replaying retained events does not corrupt current business data.
**Scope:** Consumer offset reset, replay, backfill, or reprocessing is possible.
**Checkpoints:** Idempotency; event version/time; side-effect suppression; current-state reconciliation; replay scope.
**Failure scenarios:** Historical event overwrites newer state; replay sends duplicate external notification.
**Expected behavior:** Replay is bounded, controlled, and safe for business effects.
**Evidence:** Replay procedures, consumer code, deduplication, version checks, runbooks.
**Finding criteria:** Do not assume replay is supported unless operational design indicates it; identify risks if it is available or required.
