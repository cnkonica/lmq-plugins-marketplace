#!/usr/bin/env python3
"""Prepare a local read-only GHES PR review run and dedicated worktree.

Usage:
  python3 prepare_pr_review.py 123 docs/requirements/feature-123.md
  python3 prepare_pr_review.py 123 /absolute/path/to/requirements.md --repo /path/to/repo

Requires Git, GitHub CLI (gh), and Python 3.9+. No third-party Python packages.
The script does not run project code/tests, modify application files, publish comments,
or delete worktrees.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            cmd, cwd=str(cwd) if cwd else None, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"Required executable not found: {cmd[0]}") from exc
    if check and result.returncode != 0:
        # Do not echo arbitrary command output that could contain secrets.
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Command failed ({cmd[0]}, exit {result.returncode}): {detail}")
    return result


def git_root(repo: Path) -> Path:
    result = run(["git", "rev-parse", "--show-toplevel"], cwd=repo)
    return Path(result.stdout.strip()).resolve()


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return (slug or "repo")[:48]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pr_number", type=int)
    parser.add_argument("requirements_path", type=Path)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output-root", type=Path, default=None,
                        help="Optional output root; default is <repo>/.review")
    args = parser.parse_args()

    if args.pr_number < 1:
        parser.error("PR number must be a positive integer.")

    repo = git_root(args.repo.resolve())
    req = args.requirements_path.expanduser()
    if not req.is_absolute():
        req = (repo / req).resolve()
    else:
        req = req.resolve()
    if not req.is_file():
        raise RuntimeError(f"Requirements document not found: {req}")

    # Authentication check: do not print environment/token details.
    auth = run(["gh", "auth", "status"], cwd=repo, check=False)
    if auth.returncode != 0:
        raise RuntimeError("gh auth status failed. Verify authentication to the intended GHES host.")

    fields = "number,title,url,state,baseRefName,headRefName,baseRefOid,headRefOid,headRepository,headRepositoryOwner"
    metadata_result = run(
        ["gh", "pr", "view", str(args.pr_number), "--json", fields],
        cwd=repo
    )
    metadata: dict[str, Any] = json.loads(metadata_result.stdout)
    if metadata.get("state") not in ("OPEN", "CLOSED", "MERGED"):
        raise RuntimeError(f"Unexpected PR state: {metadata.get('state')}")
    expected_head = metadata.get("headRefOid")
    expected_base = metadata.get("baseRefOid")
    if not expected_head or not expected_base:
        raise RuntimeError("PR metadata did not include both base and head SHAs.")

    repo_name = safe_slug(repo.name)
    parent = repo.parent
    suffix = uuid.uuid4().hex[:8]
    worktree = parent / f"{repo_name}-pr-review-{args.pr_number}-{suffix}"
    if worktree.exists():
        raise RuntimeError(f"Refusing to overwrite existing path: {worktree}")

    # Create worktree using gh. Do not use --force.
    run(
        ["gh", "pr", "checkout", str(args.pr_number), "--worktree", str(worktree)],
        cwd=repo
    )

    actual_head = run(["git", "rev-parse", "HEAD"], cwd=worktree).stdout.strip()
    if actual_head != expected_head:
        raise RuntimeError(
            "PR head SHA changed or worktree checkout did not match metadata. "
            f"Expected {expected_head}, got {actual_head}. Preserve the worktree and investigate; do not review."
        )

    # Re-read PR metadata after checkout to catch a moving head before capturing the patch.
    metadata_after = json.loads(run(
        ["gh", "pr", "view", str(args.pr_number), "--json", fields],
        cwd=repo
    ).stdout)
    if metadata_after.get("headRefOid") != expected_head or metadata_after.get("baseRefOid") != expected_base:
        raise RuntimeError(
            "PR base/head changed during preparation. Preserve the worktree and restart against a consistent snapshot."
        )

    patch_result = run(["gh", "pr", "diff", str(args.pr_number), "--patch"], cwd=repo)
    patch = patch_result.stdout

    output_root = args.output_root.expanduser().resolve() if args.output_root else (repo / ".review").resolve()
    # Avoid silently overwriting previous reports for the same PR.
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_root / f"PR-{args.pr_number}-{stamp}-{suffix}"
    input_dir = run_dir / "input"
    reports_dir = run_dir / "reports"
    input_dir.mkdir(parents=True, exist_ok=False)
    reports_dir.mkdir(parents=True, exist_ok=False)

    (input_dir / "pr-metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (input_dir / "pr.patch").write_text(patch, encoding="utf-8")

    manifest = {
        "createdAtUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "prNumber": args.pr_number,
        "repositoryPath": str(repo),
        "prUrl": metadata.get("url"),
        "state": metadata.get("state"),
        "baseRefName": metadata.get("baseRefName"),
        "headRefName": metadata.get("headRefName"),
        "baseSha": expected_base,
        "headSha": expected_head,
        "actualWorktreeHeadSha": actual_head,
        "requirementsPath": str(req),
        "worktreePath": str(worktree),
        "runDirectory": str(run_dir),
        "inputDirectory": str(input_dir),
        "reportsDirectory": str(reports_dir),
        "modelAssignments": {
            "gpt": "NOT_VERIFIED - set/verify in VS Code agent configuration",
            "gemini": "NOT_VERIFIED - set/verify in VS Code agent configuration"
        },
        "notes": [
            "Preparation script does not invoke AI models.",
            "Verify actual model identity and both reports before claiming two-model completion.",
            "Worktree is preserved; no automatic cleanup is performed."
        ]
    }
    (input_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print("PR review inputs prepared.")
    print(f"PR: {metadata.get('url')}")
    print(f"Base SHA: {expected_base}")
    print(f"Head SHA: {expected_head}")
    print(f"Worktree: {worktree}")
    print(f"Input directory: {input_dir}")
    print(f"Reports directory: {reports_dir}")
    print("Next: invoke the skill/Coordinator with this manifest and these paths.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
