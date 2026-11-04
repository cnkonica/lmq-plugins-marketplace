# Flex Business Data Consistency Review

## 1. Review Overview

| Item | Value |
|---|---|
| Project | |
| Review date | |
| Review scope | |
| Business flow(s) | |
| Data entities | |
| Services/components | |
| Evidence available | Design / Code / Runtime |
| Index mode | Full / Incremental / Existing |
| Rules executed | |

## 2. Executive Summary

Summarize the most material findings, overall consistency risks, and key evidence limitations. Do not claim system-wide assurance when only a subset was reviewed.

| Status / Severity | Count |
|---|---:|
| Confirmed Risk — Critical | |
| Confirmed Risk — High | |
| Confirmed Risk — Medium | |
| Confirmed Risk — Low | |
| Potential Risk | |
| Insufficient Evidence | |

## 3. Scope and Method

- Included business flows:
- Included services/components:
- Excluded areas:
- Design sources reviewed:
- Source-code areas reviewed:
- Runtime evidence reviewed:
- Review assumptions:

## 4. Business Data Flow

Describe the source of truth, owners, transformations, persistence, replicas/caches, messages, files, and downstream consumers.

```text
[Source] -> [Service] -> [Store / Event / Cache / File] -> [Consumer]
```

Identify unresolved or unverified links.

## 5. Findings

### FINDING-001 — [Concise issue title]

| Field | Value |
|---|---|
| Rule ID(s) | |
| Status | Confirmed Risk / Potential Risk / Insufficient Evidence |
| Severity | Critical / High / Medium / Low |
| Confidence | High / Medium / Low |
| Business entity | |
| Affected components | |

**Description**

What is inconsistent or at risk?

**Expected behavior / invariant**

What should be true, and what evidence establishes that expectation?

**Observed behavior / failure path**

Describe the concrete path, including relevant success/failure ordering.

**Evidence**

- Design:
- Code (file, class, method, line if available):
- Runtime:
- Missing evidence:

**Root cause**

Explain the technical cause without confusing symptoms with root cause.

**Business impact**

Describe affected data, users/processes, duration, scope, and recoverability.

**Recommendation**

Give a practical remediation or validation action. Do not prescribe a pattern unless necessary.

**Related findings / rules**

-

---

Repeat the finding section for each distinct root cause. Deduplicate symptoms caused by the same underlying issue.

## 6. Rule Coverage

| Rule ID | Applied? | Result | Evidence / Reason |
|---|---|---|---|
| | Yes / No | Finding / No Issue Found / Insufficient Evidence / Not Applicable | |

List rules not executed and why.

## 7. Evidence Gaps and Open Questions

| Question / Missing artifact | Why it matters | Owner / next action |
|---|---|---|
| | | |

## 8. Recommendations and Priority

List actions in priority order, linking each action to Finding IDs.

## 9. Conclusion

State the consistency posture within the reviewed scope, the most important risks, and what remains unverified.

## 10. Review Limitations

State explicitly:
- Areas not inspected
- Runtime evidence not provided
- Inferred versus directly observed behavior
- Index limitations
- Any assumptions that materially affect conclusions
