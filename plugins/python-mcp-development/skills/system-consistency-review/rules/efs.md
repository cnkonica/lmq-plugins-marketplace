# EFS / File Storage Data Consistency Rules

Apply these rules to file-based business data stored on EFS or an equivalent shared file system. Distinguish file contents, file metadata, and database records that reference files.

## EFS-01 — File Identity and Business Association

**Objective:** Ensure each file is associated with the correct business entity and version.
**Scope:** File path/name/metadata is linked to a business record.
**Checkpoints:** Stable business identifier; path construction; tenant isolation; uniqueness; path normalization; version identity.
**Failure scenarios:** Two entities map to same path; wrong entity references a file.
**Expected behavior:** File identity is deterministic, collision-safe, and traceable.
**Evidence:** Path builder, metadata model, naming convention, access code.
**Finding criteria:** Demonstrate collision, ambiguity, or incorrect association.

## EFS-02 — File Metadata and Physical File Consistency

**Objective:** Keep metadata records aligned with actual file existence and attributes.
**Scope:** Database stores file path, size, status, checksum, or version.
**Checkpoints:** Metadata creation/update timing; existence checks; checksum/size; status meaning; rename/move behavior.
**Failure scenarios:** DB says file is ready but file missing; file replaced but metadata points to old version.
**Expected behavior:** Metadata accurately represents file state, or asynchronous states are explicit.
**Evidence:** Metadata writes, file operations, status transitions, runtime listings/logs.
**Finding criteria:** Distinguish transient upload state from a false terminal-ready state.

## EFS-03 — Complete File Publication

**Objective:** Prevent consumers from reading partially written files as complete business artifacts.
**Scope:** Files are written and later consumed by another process.
**Checkpoints:** Temporary path then publish/rename pattern; close/flush behavior; completion marker/status; consumer readiness check; checksum/size validation where required.
**Failure scenarios:** Consumer opens file during write and processes truncated content.
**Expected behavior:** Consumers can identify only complete/published files as ready.
**Evidence:** Write/read code, naming pattern, file status, synchronization mechanism.
**Finding criteria:** Account for actual EFS semantics and application-level protocol; do not assume local filesystem guarantees beyond evidence.

## EFS-04 — Concurrent File Access

**Objective:** Prevent concurrent writers/readers from corrupting or misattributing files.
**Scope:** Multiple processes can access same path or business file.
**Checkpoints:** Unique temporary names; writer ownership; overwrite policy; atomic publication strategy; reader/writer coordination.
**Failure scenarios:** Two jobs overwrite same file; reader consumes file while writer replaces it.
**Expected behavior:** Concurrency policy protects file identity and content.
**Evidence:** Path generation, scheduler overlap controls, locks/leases, write mode, job code.
**Finding criteria:** Demonstrate a plausible race and business impact; do not require locking if naming/isolation already prevents conflict.

## EFS-05 — File Write Failure and Cross-store Partial Success

**Objective:** Handle failures between file operations and database metadata updates.
**Scope:** File and database participate in one logical business workflow.
**Checkpoints:** Failure before/during/after file write; metadata commit order; retry behavior; orphan cleanup; missing-file recovery.
**Failure scenarios:** File exists but metadata save fails; metadata says ready but file write failed.
**Expected behavior:** Partial outcomes are detectable and recoverable; ready state is truthful.
**Evidence:** File write and DB code, transaction boundaries, status records, cleanup/retry jobs.
**Finding criteria:** Do not require a distributed transaction; identify unhandled partial-success paths.

## EFS-06 — File Deletion and Retention Consistency

**Objective:** Ensure deletion, archival, and retention preserve business requirements.
**Scope:** Files and metadata have lifecycle operations.
**Checkpoints:** Delete ordering; failed deletion; metadata status; retention policy; legal/business retention; retry and orphan detection.
**Failure scenarios:** Metadata removed but file remains; file deleted while still referenced.
**Expected behavior:** Lifecycle and retention semantics are explicit and recoverable.
**Evidence:** Delete code, cleanup jobs, retention config, references, logs.
**Finding criteria:** Orphan files may be acceptable under retention policy; verify requirements before reporting.

## EFS-07 — Duplicate File Creation and Retry Safety

**Objective:** Prevent retries from creating unintended duplicate or conflicting files.
**Scope:** File generation/upload can be retried.
**Checkpoints:** Stable operation/file ID; deterministic path; overwrite/version policy; duplicate detection; metadata uniqueness.
**Failure scenarios:** Retry creates multiple files for one logical artifact or overwrites newer file.
**Expected behavior:** Retry produces the intended same artifact/version or a clearly versioned new artifact.
**Evidence:** Naming logic, request IDs, generation job, metadata constraints, retry code.
**Finding criteria:** Consider whether multiple versions are intentionally retained.

## EFS-08 — File Version and Replacement Consistency

**Objective:** Ensure database references and consumers identify the intended file version.
**Scope:** Files can be regenerated, replaced, or versioned.
**Checkpoints:** Version identifier; immutable versus mutable path; metadata update; reader caching; old version retention.
**Failure scenarios:** DB points to new version while consumer reads old path/content.
**Expected behavior:** Version selection is explicit and consistent.
**Evidence:** Version fields, path construction, update logic, consumer reads.
**Finding criteria:** Report only where version ambiguity can affect business correctness.

## EFS-09 — File Integrity and Recovery

**Objective:** Detect corruption, truncation, or missing files and recover safely.
**Scope:** File integrity is material to business processing.
**Checkpoints:** Checksums, size/format validation, backup/replication assumptions, retry/regeneration source, recovery status.
**Failure scenarios:** Corrupt file marked valid; no source exists to regenerate lost artifact.
**Expected behavior:** Integrity checks and recovery meet business criticality.
**Evidence:** Validation code, checksum metadata, backup/runbook, generation source, runtime evidence.
**Finding criteria:** Do not demand checksums for every file; assess risk and reproducibility.

## EFS-10 — File Lifecycle and Temporary Artifacts

**Objective:** Prevent temporary, failed, or expired artifacts from being mistaken for valid business files.
**Scope:** Temporary/staging/final files or lifecycle states exist.
**Checkpoints:** Naming/extension conventions; staging/final separation; cleanup; state transition; consumer filtering; retention.
**Failure scenarios:** Consumer processes a temporary file; abandoned staging files accumulate and are referenced.
**Expected behavior:** Artifact states are distinguishable and cleanup is safe.
**Evidence:** File naming, directory layout, consumers, cleanup jobs, metadata status.
**Finding criteria:** Temporary files are not defects merely because they exist; assess discoverability and business impact.
