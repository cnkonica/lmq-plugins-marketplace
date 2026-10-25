# GHES Multi-Model PR Review Skill

A VS Code Agent Skill package for local, read-only, multi-model PR review on GitHub Enterprise Server.

## Contents

- `SKILL.md`: Main workflow and skill entry point.
- `scripts/prepare_pr_review.py`: Fetches PR metadata and patch, creates a dedicated worktree, and records a manifest.
- `references/`: Shared review methodology and safety rules.
- `templates/`: Markdown report templates.
- `agents/`: Custom Agent configuration templates to copy into `.github/agents/`.

## Install the skill

Copy this directory:

`.github/skills/ghes-multimodel-pr-review/`

into the target repository at:

`.github/skills/ghes-multimodel-pr-review/`

VS Code Agent Skills are discovered from `.github/skills/<skill-name>/SKILL.md` when the selected agent/harness supports workspace skills. The `name` field must match the directory name.

## Install agent templates separately

The files under `agents/` are templates, not active custom agents while they remain inside this skill folder. If you want VS Code to discover them as custom agents, copy them to:

`.github/agents/pr-review-coordinator.agent.md`
`.github/agents/gpt-reviewer.agent.md`
`.github/agents/gemini-reviewer.agent.md`
`.github/agents/review-aggregator.agent.md`

Then replace the model placeholders with identifiers actually supported by the VS Code model picker and your active harness. Confirm that the coordinator can delegate to the two reviewer agents. A skill does not itself guarantee model routing or subagent execution.

## Prerequisites

- Git.
- GitHub CLI (`gh`) installed and authenticated to the expected GHES host.
- Python 3.9+ (standard library only) to run the preparation script.
- VS Code with an agent/harness that supports Agent Skills.
- Company approval to process the repository and requirements with the selected models.

## Run

From the repository root:

`python3 .github/skills/ghes-multimodel-pr-review/scripts/prepare_pr_review.py 123 docs/requirements/feature-123.md`

This prepares inputs and a worktree. It does not itself invoke AI models. Invoke `/ghes-multimodel-pr-review` in the supported VS Code Chat experience and provide the PR number and requirements path, or use the configured Coordinator Agent.

## Important limitations

- `gh` retrieves PR data but does not call Copilot models.
- Chat model availability does not automatically guarantee that custom subagents can be bound to those models.
- Confirm actual model identity and report provenance at runtime.
- The script intentionally does not run tests, build the project, modify application code, publish PR comments, or delete the worktree.
