# Requirements Review Method

## Goal

Determine whether the actual behavior of the PR satisfies the explicit requirements and acceptance criteria. Do not turn a requirements review into a style review.

## Procedure

1. Read the approved requirements document and identify its version or revision if available.
2. Extract explicit functional requirements, business rules, constraints, validation rules, error behavior, and acceptance criteria.
3. Split compound statements into atomic, independently verifiable requirements.
4. Assign stable IDs such as `REQ-001`, `REQ-002`.
5. For each requirement, identify the relevant PR changes and trace the actual implementation through callers, services, domain logic, persistence, external integrations, configuration, and tests.
6. Compare expected behavior with actual behavior.
7. Check boundary cases and failure paths implied by the requirements.
8. Record test coverage separately from implementation compliance.
9. Mark ambiguities as clarification questions instead of inventing an interpretation.
10. Revisit any apparent missing implementation in unchanged code before reporting a gap.

## Status definitions

- `PASS`: Sufficient evidence supports compliance.
- `PARTIAL`: Some explicit behavior or scenarios are missing.
- `FAIL`: Evidence demonstrates missing or incorrect required behavior.
- `UNVERIFIED`: Evidence is insufficient to determine compliance.
- `NOT APPLICABLE`: The requirement does not apply, with justification.

## Required traceability matrix

| Requirement ID | Requirement / acceptance criterion | Implementation evidence | Status | Gap / note |
|---|---|---|---|---|

## Defect report fields

For each confirmed requirement defect:
- Finding ID.
- Severity.
- Requirement ID and source section.
- File and line.
- Evidence.
- Expected behavior.
- Actual behavior.
- Concrete failure scenario.
- Business impact.
- Recommended correction.
- Confidence.

## Rules

- Do not invent requirements.
- Do not assume a requirement is missing merely because it is absent from the diff.
- Do not mark a requirement `FAIL` only because no test exists.
- Do not prescribe an implementation technology unless required by the specification or a demonstrated constraint.
- Separate implementation defects, missing tests, ambiguous requirements, and unverified items.
- Report the requirement document path and revision/hash when available.
