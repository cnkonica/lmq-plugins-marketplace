# Flex Business Data Consistency Review

## 1. Objective

Analyze whether business data in the Flex project remains correct, complete, and consistent across services and components throughout its lifecycle.

The review focuses on:
- Technical design and data contracts
- Source-code behavior
- Available runtime evidence
- End-to-end and cross-component data flows

This is a read-only, human-triggered review skill. It must not modify application source code, business data, or production systems.

## 2. Core Principles

1. **Business outcome over technology checklist.** A technology configuration is relevant only when it affects a business-data invariant or a documented operational requirement.
2. **Rule-driven.** Every finding must map to one or more applicable rules in `rules/`.
3. **Evidence-based.** Do not infer runtime facts from source code alone.
4. **Scope-aware.** State which business flows, services, components, files, and evidence were actually reviewed.
5. **No assumption of synchronous consistency.** Eventual consistency may be valid when the business contract defines an acceptable delay and recovery behavior.
6. **Read-only.** Do not connect to production databases, alter data, change code, or trigger business operations.

## 3. Package Layout

- `index/project-index.json`: generated project navigation index. It is a local artifact for the project being reviewed.
- `rules/`: authoritative review criteria.
- `scripts/project-index.py`: index generation and update utility.
- `templates/review-report.md`: report structure.
- `DESIGN.md` at the package root: full design and operating guide.

If one Skill installation is shared by multiple projects, keep a separate working copy of the Skill package (including `index/project-index.json`) per project. Do not let multiple projects overwrite one shared index.

## 4. Review Workflow

### Step 1 — Establish scope
Identify the requested business process, data entities, services, environments, and available evidence. If the user gives a narrow scope, do not silently expand it to the whole system.

### Step 2 — Update Project Index
Run the index script against the Flex project root:

```bash
python /path/to/flex-consistency-review/scripts/project-index.py --root /path/to/Flex
```

The script automatically chooses full or incremental indexing. Use `--force` only when a rebuild is needed. The index is a navigation aid, not proof of behavior.

### Step 3 — Discover business data and ownership
Identify:
- Business entities and identifiers
- Authoritative source of truth for each entity
- Services that create, read, update, or delete the entity
- State fields and permitted transitions
- Copies, caches, events, files, and derived representations

Do not assume a data owner solely from a class name or repository location; verify actual write paths and design evidence.

### Step 4 — Trace end-to-end data flows
Trace the relevant path from initiating request or scheduled process through service boundaries, persistence, messaging, cache, and file storage. Follow calls and event handlers where evidence permits. Record unresolved links.

### Step 5 — Select applicable rules
Always consider relevant core and cross-component rules in `rules/cross-component.md`. Load technology-specific files only for technologies and behaviors evidenced in the scoped project. Do not run every rule mechanically.

A rule is applicable only when its stated scope and preconditions are met. Mark it `Not Applicable` with a short reason when appropriate.

### Step 6 — Analyze three evidence dimensions
- **Design:** architecture documents, data models, API/event contracts, sequence diagrams, requirements.
- **Code:** implementations, repositories, queries, event producers/consumers, cache operations, file operations, exception and retry paths.
- **Runtime:** only logs, data samples, metrics, execution records, or environment observations actually supplied or explicitly accessible.

For each rule, compare expected behavior with observed design/code/runtime evidence. If a dimension is unavailable, say so. Never claim runtime consistency based only on static code.

### Step 7 — Validate findings
For each candidate issue:
- Identify the business invariant or documented requirement at risk.
- Describe a concrete failure path.
- Cite exact evidence (file path, class/method, line range when available, or runtime artifact).
- Check alternate paths, shared helpers, listeners, retries, and compensating behavior before concluding.
- Deduplicate findings that share one root cause.
- Separate confirmed defects from plausible risks and evidence gaps.

### Step 8 — Generate report
Use `templates/review-report.md`. Include scope, components, rules executed, data-flow summary, findings, rule coverage, missing evidence, conclusion, and limitations.

## 5. Finding Status, Severity, and Confidence

### Status
- **Confirmed Risk:** evidence demonstrates a violation of a business invariant or documented requirement, or demonstrates an actual inconsistent state.
- **Potential Risk:** a credible failure path exists in design/code, but occurrence or a key condition is not confirmed.
- **Insufficient Evidence:** essential design, code path, or runtime information is unavailable.
- **No Issue Found:** no issue was identified within the stated scope and evidence reviewed. This is not proof that the whole system is defect-free.
- **Not Applicable:** rule preconditions are not met.

### Severity
- **Critical:** likely to cause broad or materially irreversible business-data loss/corruption, or severe business decisions based on invalid data.
- **High:** important business data can become inconsistent, duplicated, missing, or stale with material impact; recovery is difficult or delayed.
- **Medium:** bounded inconsistency or integrity risk with limited impact and a feasible recovery path.
- **Low:** minor integrity/maintainability risk with low business impact.

Severity must be based on business impact, scope, likelihood, duration, and recoverability—not on technology choice alone.

### Confidence
- **High:** evidence chain is direct and key assumptions are verified.
- **Medium:** strong evidence exists but some relevant context remains unverified.
- **Low:** evidence is indirect or incomplete; prefer `Potential Risk` or `Insufficient Evidence`.

## 6. Evidence and Citation Requirements

Every finding must contain:
- Rule ID(s)
- Affected business entity and components
- Evidence references (file path and class/method; line numbers if available)
- Concrete failure scenario or observed inconsistency
- Expected behavior and why observed behavior differs
- Business impact
- Practical recommendation
- Status, severity, and confidence

Do not invent line numbers, logs, runtime values, architecture decisions, or requirements. Clearly label assumptions and open questions.

## 7. Rule Execution Discipline

Each rule file defines objective, scope, preconditions, checkpoints, failure scenarios, expected behavior, evidence, and finding criteria.

- Follow the rule's `Finding Criteria`; a checkpoint is a prompt for investigation, not automatic proof of a defect.
- Do not report a missing mechanism unless the business requirement or risk scenario makes it necessary.
- Do not require distributed transactions, Kafka, Redis, or a particular design pattern by default.
- Consider business-approved eventual consistency and documented tolerances.
- Look for compensating paths and recovery jobs before reporting a failure.
- Reuse evidence across related rules, but create one primary finding per root cause and reference related Rule IDs.
- Report unexecuted rules and reasons; do not imply full coverage.

## 8. Index Limitations

The index script performs file discovery and lightweight text-based technology-signal detection. It does not build a complete AST, call graph, data lineage graph, or proof of execution. Always inspect source files and relevant references before making findings.
