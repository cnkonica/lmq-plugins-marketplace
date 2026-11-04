# Flex Business Data Consistency Review — Design Document

## 1. Purpose

This document describes the first-version design of the `flex-consistency-review` Skill. The purpose is to review business-data correctness, completeness, and consistency across Flex services and components.

The Skill is rule-driven and evidence-based. It reviews technical design, source code, and available runtime evidence, then produces a structured report.

## 2. Goals and Non-goals

### Goals
- Establish explicit, reusable business-data consistency rules.
- Locate relevant project files through a lightweight Project Index.
- Trace business data across services, databases, caches, messaging, and file storage.
- Compare expected behavior with design, implementation, and available runtime evidence.
- Produce actionable findings with evidence, impact, severity, and recommendations.

### Non-goals for version 1
- Scheduled or unattended review automation.
- Production database connections or production data mutation.
- Automatic code changes or data repair.
- Multi-agent orchestration.
- Full AST parsing, call-graph generation, or formal proof.
- CI/CD integration or a historical findings database.

## 3. Directory Structure

```text
flex-consistency-review/
├── SKILL.md
├── index/
│   └── project-index.json
├── rules/
│   ├── mongodb.md
│   ├── redis.md
│   ├── kafka.md
│   ├── efs.md
│   └── cross-component.md
├── scripts/
│   └── project-index.py
└── templates/
    └── review-report.md
```

This package also contains this `DESIGN.md` at the ZIP root, alongside the Skill directory.

### File responsibilities

| File | Responsibility |
|---|---|
| `SKILL.md` | Entry point, workflow, rule selection, evidence and report requirements |
| `index/project-index.json` | Generated navigation index for one project |
| `scripts/project-index.py` | Full/incremental index generation and status inspection |
| `rules/cross-component.md` | Core business consistency rules across component boundaries |
| `rules/mongodb.md` | MongoDB-specific consistency checks |
| `rules/redis.md` | Redis role/cache/state consistency checks |
| `rules/kafka.md` | Event publication/consumption consistency checks |
| `rules/efs.md` | File and metadata consistency checks |
| `templates/review-report.md` | Standard report layout |

## 4. Rule Architecture

Rules are the primary quality asset of this Skill. They are not generic technology best-practice checklists. A rule must connect a technical behavior to a business-data invariant or requirement.

### 4.1 Rule layers

1. **Core business consistency:** ownership, definition, mapping, completeness, lifecycle, state transitions, synchronization, partial success, idempotency, ordering, recovery, reconciliation, eventual consistency.
2. **Technology-specific:** MongoDB, Redis, Kafka, and EFS behaviors that can affect those invariants.
3. **Cross-component application:** apply the core principles to complete business flows crossing service and technology boundaries.

The current package keeps the original five-file structure. The core principles are included in `cross-component.md` to avoid introducing another file in version 1.

### 4.2 Required rule structure

Every rule should specify:
- Rule ID and name
- Objective
- Scope and preconditions
- Checkpoints
- Failure scenarios
- Expected behavior
- Evidence to inspect
- Finding criteria

A checkpoint is an investigation prompt, not automatic proof of a defect. Finding criteria control whether evidence is sufficient to report a risk.

### 4.3 Rule quality controls

Before treating the rule set as validated, perform:
- **Coverage validation:** ensure major consistency domains are represented.
- **Scenario validation:** test rules against realistic failure paths.
- **False-positive validation:** ensure accepted eventual consistency and valid architecture choices are not incorrectly flagged.
- **Evidence validation:** ensure findings require concrete evidence and consider alternate paths.
- **Overlap validation:** deduplicate rules that cover the same root cause at different layers.

The rules in this package are a structured baseline. They must be validated against Flex's actual architecture, requirements, code, and operational evidence before claiming complete project coverage.

## 5. Project Index Design

### 5.1 Purpose

The Project Index is a navigation aid that helps identify candidate files and technology signals. It is not a complete parser, dependency graph, call graph, data lineage graph, or proof of runtime behavior.

### 5.2 Location

The requested design places `index/project-index.json` inside the Skill directory. When using the Skill with one project, keep a project-specific Skill working copy. If the same Skill is used for multiple projects, use separate working copies/indexes to prevent one project from overwriting another's index.

The script defaults the index path to `<project-root>/index/project-index.json`. Therefore, for the requested in-Skill location, pass `--index` explicitly to the Skill package's index file:

```bash
python /path/to/flex-consistency-review/scripts/project-index.py \
  --root /path/to/Flex \
  --index /path/to/flex-consistency-review/index/project-index.json
```

This distinction is intentional: the project root is scanned, while the index output is stored in the Skill package.

### 5.3 Full versus incremental

The script automatically chooses:
- **Full:** index missing/invalid, forced rebuild, index version changed, scan configuration version changed, or project root changed.
- **Incremental:** valid compatible index exists for the same project root.

Incremental mode still walks the current file tree to discover additions and deletions. It calculates SHA-256 for discovered files and re-runs text-signal analysis only for new or changed files. Unchanged entries are retained; deleted paths are removed.

Commands:

```bash
# Automatic full/incremental decision; keep index in Skill folder
python scripts/project-index.py --root /path/to/Flex \
  --index /path/to/flex-consistency-review/index/project-index.json

# Force full rebuild
python scripts/project-index.py --root /path/to/Flex \
  --index /path/to/flex-consistency-review/index/project-index.json \
  --force

# Inspect index without updating
python scripts/project-index.py --root /path/to/Flex \
  --index /path/to/flex-consistency-review/index/project-index.json \
  --status
```

### 5.4 Safety and limitations

- Uses only Python standard library.
- Excludes common generated/vendor directories.
- Scans selected code/config/document suffixes and skips files larger than 2 MB.
- Writes to a temporary file, validates JSON, then atomically replaces the index.
- If scanning or writing fails, it does not intentionally replace the prior index.
- Text-signal matching is heuristic and may miss indirect references or produce false positives.
- A changed file is re-analyzed; an unchanged file retains its previous extracted signals.
- If detection logic changes, increment `SCAN_CONFIG_VERSION` to force a rebuild.
- The index should be treated as derived, project-specific data. Whether it is committed to Git is a team decision; generated indexes can become stale or cause merge conflicts.

## 6. Review Method

### 6.1 Establish the business invariant

For each scoped business entity/flow, identify what must remain true. Examples include unique business identity, allowed state transitions, required fields, source-of-truth ownership, or a defined freshness tolerance.

Do not invent requirements. If the invariant is unclear, record an evidence gap or question.

### 6.2 Trace data

Trace the data from origin through:
- API/request or scheduler
- Service/business logic
- Database persistence
- Cache or derived views
- Event publication and consumption
- File creation/metadata
- Downstream consumers

Record owner, identifier, transformations, state transitions, and failure boundaries.

### 6.3 Review three evidence dimensions

| Dimension | Evidence examples | What it can establish |
|---|---|---|
| Design | requirements, architecture docs, data models, API/event contracts | Intended behavior and business invariants |
| Code | methods, queries, event handlers, retries, file operations | Implemented paths and possible failure windows |
| Runtime | supplied logs, samples, metrics, execution records | Observed behavior in the represented environment/time |

Code cannot prove what happened in production. Runtime samples cannot by themselves establish all possible code paths. Cross-check dimensions where available.

## 7. Finding Model

### Status
- Confirmed Risk
- Potential Risk
- Insufficient Evidence
- No Issue Found
- Not Applicable

### Severity
- Critical
- High
- Medium
- Low

Severity is based on business impact, affected scope, likelihood, duration, and recoverability.

### Confidence
- High
- Medium
- Low

Confidence expresses evidence strength, not business severity.

### Deduplication
One underlying root cause should normally produce one primary finding. Related rules can be listed together rather than creating duplicate findings.

## 8. Efficiency Strategy

- Use Project Index for candidate discovery, then inspect actual source.
- Load only technology rules relevant to the scoped flow.
- Always consider relevant cross-component rules.
- Scope analysis to the requested business flow.
- Reuse evidence across related rules.
- Deduplicate findings by root cause.
- Do not add incremental-review caching in version 1; only indexing is incremental.

## 9. Validation and Acceptance

A first release should be accepted only after:
1. Index full generation works.
2. Incremental mode detects additions, modifications, and deletions.
3. Invalid or incompatible index triggers a full rebuild.
4. Index update is safe and atomic.
5. Each rule has the required definition fields.
6. Rules are checked for overlap and applicability.
7. Representative Flex failure scenarios are used to validate detection.
8. False-positive cases (especially valid eventual consistency) are tested.
9. Findings include evidence, business impact, and limitations.
10. Report clearly distinguishes confirmed, potential, and unverified issues.

## 10. Known Limitations and Future Decisions

- The initial rules are a baseline, not a claim of exhaustive Flex coverage.
- The index is heuristic and does not understand all Java/Kotlin call relationships.
- Runtime review depends on evidence supplied or explicitly made available.
- The in-Skill index location requires project-specific Skill copies or a disciplined per-project index path.
- Rule coverage and wording should be refined after examining Flex's actual data flows and requirements.
- Future enhancements should be justified by observed gaps, not added preemptively.
