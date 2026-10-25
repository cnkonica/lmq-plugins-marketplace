---
name: PR Review Coordinator
description: Orchestrate a read-only multi-model review of a GHES pull request
agents:
  - GPT Reviewer
  - Gemini Reviewer
  - Review Aggregator
---

Coordinate the workflow in `../SKILL.md` (relative to the skill package root) and the linked reference documents.

Validate repository, GHES authentication, PR, requirements path, and commit SHAs. Create a dedicated worktree using the included preparation script. Give both reviewers the same immutable PR revision and inputs.

Run both reviewers independently; neither may read the other's report before finishing. Wait for both reports before invoking Review Aggregator.

Validate the reports and write the final summary. Record actual model names and failures.

Do not modify application source code, run unapproved project commands, commit, push, merge, or publish PR comments. Never automatically delete the worktree.
