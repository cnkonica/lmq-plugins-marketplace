# Redis Data Consistency Rules

First classify each Redis use: cache, session, lock, counter, queue, deduplication/idempotency store, or authoritative business state. Do not apply cache rules to non-cache uses without adapting the scope.

## RED-01 — Redis Data Role and Ownership

**Objective:** Establish whether Redis is a cache, derived view, coordination mechanism, or authoritative store.
**Scope:** Redis keys participate in business flows.
**Checkpoints:** Identify key owners, writers/readers, source of truth, persistence expectations, and permitted loss.
**Failure scenarios:** A disposable cache is treated as authoritative; multiple writers conflict.
**Expected behavior:** Role and durability/consistency expectations are explicit.
**Evidence:** Key usage, service code, Redis config, design docs.
**Finding criteria:** Report role ambiguity only when it creates a credible business-data risk.

## RED-02 — Key Identity and Data Contract

**Objective:** Ensure key construction and serialized values map to the correct business entity and schema.
**Scope:** Redis stores entity-related values.
**Checkpoints:** Key namespace, tenant/entity identifiers, collisions, value schema/version, serialization, field semantics.
**Failure scenarios:** Key collision across tenants; incompatible serializer reads wrong structure.
**Expected behavior:** Key and value identity are deterministic and compatible.
**Evidence:** Key builders, serializers, DTOs, configuration, sample keys.
**Finding criteria:** Require a concrete collision or compatibility risk.

## RED-03 — Source-to-Cache Synchronization

**Objective:** Keep cached representations aligned with the authoritative source within the required freshness contract.
**Scope:** Redis caches data stored authoritatively elsewhere.
**Checkpoints:** Write-through/aside/behind strategy; update/delete paths; cache invalidation; failure between DB and cache; retry/rebuild.
**Failure scenarios:** Database update succeeds while cache remains stale.
**Expected behavior:** Cache update/invalidation is reliable or stale data is bounded and recoverable.
**Evidence:** Database write path, cache operations, events, retry logic, freshness requirements.
**Finding criteria:** A DB/cache timing gap alone is not a defect if the consistency contract permits it.

## RED-04 — Cache Invalidation and Lifecycle

**Objective:** Prevent obsolete cache entries from surviving business updates, deletion, or expiry.
**Scope:** Cache entries represent mutable or deletable business data.
**Checkpoints:** All mutation paths invalidate/update keys; delete/rename paths; wildcard/version invalidation; TTL; negative cache behavior.
**Failure scenarios:** Deleted entity remains readable; one update path forgets invalidation.
**Expected behavior:** Cache lifecycle follows source entity lifecycle and freshness policy.
**Evidence:** All writers, invalidation methods, key patterns, TTL config.
**Finding criteria:** Trace all relevant mutation paths before reporting missing invalidation.

## RED-05 — Stale Reads and Freshness Boundaries

**Objective:** Ensure consumers do not use stale data beyond permitted business tolerance.
**Scope:** Cache may lag authoritative data.
**Checkpoints:** Maximum tolerated staleness; cache age/version; read-after-write behavior; critical decisions using cached values.
**Failure scenarios:** Stale balance/permission/status used for a critical decision.
**Expected behavior:** Freshness policy matches business criticality.
**Evidence:** Requirements, TTL, cache refresh, version/timestamp, read paths.
**Finding criteria:** Do not assign severity based only on TTL; assess actual business use and tolerance.

## RED-06 — TTL and Expiration Semantics

**Objective:** Ensure expiration does not remove required state too early or retain data beyond its intended validity.
**Scope:** TTL is used for business-relevant Redis keys.
**Checkpoints:** TTL source and units; refresh behavior; expiration races; missing TTL; expiry relative to business validity.
**Failure scenarios:** Idempotency key expires before retry window; session or workflow state expires prematurely.
**Expected behavior:** TTL aligns with documented business/operational lifetime.
**Evidence:** `EXPIRE`/TTL calls, config, retry windows, requirements.
**Finding criteria:** No universal TTL is correct; compare configured lifetime with actual requirement.

## RED-07 — Concurrent Cache Updates

**Objective:** Prevent stale concurrent writes from overwriting newer cache state.
**Scope:** Multiple writers or asynchronous updates affect the same key.
**Checkpoints:** Read-modify-write; atomic Redis operations/scripts; version checks; event ordering; invalidation races.
**Failure scenarios:** Slow old request writes old value after newer update.
**Expected behavior:** Concurrency semantics preserve required freshness/order.
**Evidence:** Redis commands, scripts, version fields, call paths, event handlers.
**Finding criteria:** Demonstrate a feasible interleaving and impact.

## RED-08 — Redis Failure and Fallback Behavior

**Objective:** Ensure Redis outages do not silently corrupt or misrepresent business data.
**Scope:** Redis availability affects reads/writes or workflow coordination.
**Checkpoints:** Cache bypass/fallback; write failure behavior; fail-open/fail-closed decision; fallback source; recovery after outage.
**Failure scenarios:** Business operation reports success but required state was not persisted; fallback returns incompatible data.
**Expected behavior:** Failure policy is explicit and appropriate to Redis role.
**Evidence:** Exception handling, timeout config, fallback code, service requirements.
**Finding criteria:** Evaluate cache versus lock/session/authoritative use separately.

## RED-09 — Serialization and Schema Evolution

**Objective:** Ensure values remain readable and semantically compatible across deployments.
**Scope:** Redis values are serialized or shared across application versions.
**Checkpoints:** Serializer configuration; type compatibility; schema/version; rolling deployment compatibility; null/default handling.
**Failure scenarios:** New version cannot read old cached value; different services serialize same key differently.
**Expected behavior:** Compatible evolution or safe invalidation/rebuild.
**Evidence:** Serializer config, DTOs, deployment strategy, key versioning.
**Finding criteria:** Report demonstrated incompatibility or unsafe rollout path.

## RED-10 — Cache Rebuild and Recovery

**Objective:** Ensure disposable or derived Redis data can be reconstructed safely when lost or flushed.
**Scope:** Redis data is derived or expected to be recoverable.
**Checkpoints:** Authoritative source; rebuild path; completeness; rebuild concurrency; stale data during rebuild.
**Failure scenarios:** Cache flush leaves service permanently incomplete; rebuild mixes old/new snapshots.
**Expected behavior:** Rebuild restores a correct representation or failure is explicitly handled.
**Evidence:** Warm-up jobs, rebuild code, source queries, operational runbooks.
**Finding criteria:** Do not require rebuild for intentionally ephemeral state; verify expected durability.
