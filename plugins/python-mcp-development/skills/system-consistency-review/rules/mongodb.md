# MongoDB Data Consistency Rules

Apply these rules only where MongoDB is actually used in the scoped business flow. MongoDB-specific implementation choices are not defects by themselves; assess them against business invariants and the required consistency behavior.

## MDB-01 — Collection and Data Ownership

**Objective:** Identify the authoritative owner of documents and collections.

**Scope:** Multiple services or jobs access the same collection/entity.

**Checkpoints:** Identify writers and readers; verify owner; inspect cross-service writes; distinguish authoritative data from projections.
**Failure scenarios:** Uncoordinated writers; service updates fields owned by another service.
**Expected behavior:** Ownership and write responsibility are explicit.
**Evidence:** Repository usage, service methods, configuration, design docs.
**Finding criteria:** Report conflicting or uncontrolled writes, not merely shared read access.

## MDB-02 — Document Schema and Field Semantics

**Objective:** Preserve field meaning, type, nullability, and requiredness.
**Scope:** Documents are created, updated, serialized, or consumed by multiple code paths.
**Checkpoints:** Compare DTO/entity/document definitions; inspect defaults, null handling, enum values, numeric precision, date/time representation, schema evolution.
**Failure scenarios:** One writer stores string while another expects number; missing field silently becomes zero; incompatible enum.
**Expected behavior:** Writers/readers agree on field semantics or explicitly migrate/convert.
**Evidence:** Models, validators, serializers, mapping code, sample documents.
**Finding criteria:** Require a concrete semantic mismatch or credible incompatible path.

## MDB-03 — Create, Update, Delete, and Lifecycle Semantics

**Objective:** Ensure document lifecycle operations preserve business state.
**Scope:** Entity lifecycle is represented in MongoDB.
**Checkpoints:** Inspect create/upsert behavior; soft-delete/hard-delete semantics; update field selection; dependent references; archival/retention; repeated deletion.
**Failure scenarios:** Upsert creates unintended entity; deleted entity remains active in related collection.
**Expected behavior:** Lifecycle follows business requirements and dependent data handling.
**Evidence:** Repository methods, query filters, update operators, lifecycle docs.
**Finding criteria:** Do not assume cascade delete is required; verify intended lifecycle.

## MDB-04 — Atomicity and Multi-document Workflows

**Objective:** Identify partial writes that violate a business invariant.
**Scope:** One logical operation changes multiple documents or collections.
**Checkpoints:** Determine invariant; inspect transaction boundaries; identify partial-success windows; inspect compensation/retry/reconciliation.
**Failure scenarios:** First document commits, second fails, leaving inconsistent state.
**Expected behavior:** Required atomicity is achieved or partial completion is durable and recoverable.
**Evidence:** Session/transaction use, service flow, status records, recovery code.
**Finding criteria:** Do not require a transaction where eventual consistency or a recoverable workflow is valid.

## MDB-05 — Write Idempotency and Duplicate Prevention

**Objective:** Prevent repeated writes from creating unintended duplicate business records/effects.
**Scope:** Create/update operations can be retried or invoked more than once.
**Checkpoints:** Stable business key; upsert/filter semantics; unique indexes; request deduplication; side effects around writes.
**Failure scenarios:** Retry after timeout inserts a second document.
**Expected behavior:** Retry semantics match business requirements.
**Evidence:** Query filters, unique indexes, request identifiers, retry logic.
**Finding criteria:** A missing unique index is not automatically a defect; demonstrate a duplicate path and required uniqueness.

## MDB-06 — Concurrent Updates and Lost Updates

**Objective:** Prevent concurrent writers from silently overwriting business changes.
**Scope:** Multiple requests/jobs may update the same document or related documents.
**Checkpoints:** Read-modify-write pattern; atomic operators; version field; conditional filters; transaction/locking strategy where needed.
**Failure scenarios:** Two updates read same old value and one overwrites the other.
**Expected behavior:** Concurrent operations preserve required invariants.
**Evidence:** Update queries, filters, versioning, transaction code, concurrency tests.
**Finding criteria:** Show a plausible interleaving and affected invariant; do not require locks universally.

## MDB-07 — Uniqueness and Business Identity

**Objective:** Ensure business identity constraints are enforced where required.
**Scope:** A business key must identify one logical record.
**Checkpoints:** Identify natural/business key; inspect unique indexes and compound key scope; account for soft deletes/tenant scope; handle duplicate-key errors.
**Failure scenarios:** Two documents represent one business entity.
**Expected behavior:** Required uniqueness is enforced consistently.
**Evidence:** Index definitions, schema migrations, insert/upsert code, duplicate handling.
**Finding criteria:** Only report missing enforcement when uniqueness is a business requirement and concurrent creation can violate it.

## MDB-08 — References and Referential Integrity

**Objective:** Prevent invalid or dangling relationships between documents.
**Scope:** Documents reference other documents by identifier.
**Checkpoints:** Validate referenced entity existence/status; inspect lifecycle handling; handle cross-collection updates; identify orphan detection.
**Failure scenarios:** Child document points to deleted or wrong parent.
**Expected behavior:** Relationships follow the defined lifecycle and integrity rules.
**Evidence:** Reference fields, lookup/query code, delete/update paths, reconciliation.
**Finding criteria:** MongoDB does not enforce relational foreign keys; assess application-level requirements.

## MDB-09 — Read Consistency and Query Semantics

**Objective:** Ensure reads return data appropriate to the business operation.
**Scope:** Reads use replicas, multiple queries, aggregation, or cached/derived views.
**Checkpoints:** Read preference/concern where configured; stale read tolerance; pagination/sort stability; filters and tenant scoping; multi-query snapshot assumptions.
**Failure scenarios:** A decision uses stale or incomplete data; pagination skips/duplicates records under concurrent updates.
**Expected behavior:** Read semantics meet the business freshness and completeness contract.
**Evidence:** Mongo client config, query code, aggregation, API requirements, runtime samples.
**Finding criteria:** Do not assume primary reads or strongest read concern are always required.

## MDB-10 — Partial Updates and Field Preservation

**Objective:** Prevent updates from unintentionally erasing or defaulting unrelated fields.
**Scope:** Partial DTOs, patch operations, bulk updates, or object replacement are used.
**Checkpoints:** `$set` versus replacement; null versus absent semantics; mapper behavior; update field allowlist; bulk partial failure.
**Failure scenarios:** Partial request replaces full document; omitted field becomes null/default.
**Expected behavior:** Only intended fields change; partial failure is visible.
**Evidence:** Update operators, mapping code, API semantics, bulk write handling.
**Finding criteria:** Demonstrate an unintended field mutation or credible mapping path.
