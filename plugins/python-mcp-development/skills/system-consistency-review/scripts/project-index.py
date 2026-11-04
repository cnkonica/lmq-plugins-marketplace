#!/usr/bin/env python3
"""Build or incrementally update a lightweight, read-only project navigation index.

The index is a navigation aid, not an AST/call graph or proof of runtime behavior.
Uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INDEX_VERSION = 1
SCAN_CONFIG_VERSION = 1
DEFAULT_INDEX_RELATIVE = Path("index") / "project-index.json"

EXCLUDED_DIRS = {
    ".git", ".idea", ".gradle", ".project-index", ".venv", "venv",
    "__pycache__", "node_modules", "target", "build", "dist", "out",
    ".next", ".terraform", "coverage"
}
INCLUDED_SUFFIXES = {
    ".java", ".kt", ".kts", ".groovy", ".py", ".js", ".jsx", ".ts", ".tsx",
    ".xml", ".yml", ".yaml", ".properties", ".json", ".toml", ".sql",
    ".md", ".gradle", ".sh", ".tf", ".conf", ".config", ".proto"
}
MAX_SCAN_BYTES = 2_000_000

SIGNALS = {
    "mongodb": ("mongodb", "mongoTemplate", "mongorepository", "mongoRepository"),
    "redis": ("redis", "redistemplate", "stringredisTemplate".lower(), "jedis", "lettuce"),
    "kafka": ("kafka", "kafkatemplate", "@kafkalistener", "kafkalistener"),
    "efs": ("efs", "elastic file system", "amazonelasticfilesystem", "nfs"),
    "spring-boot": ("springboot", "spring-boot", "@springbootapplication"),
    "s3": ("s3client", "amazon s3", "s3bucket"),
    "database": ("jdbc", "jpa", "repository", "datasource", "sql"),
}

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()

def discover_files(root: Path, index_path: Path) -> list[Path]:
    found: list[Path] = []
    index_resolved = index_path.resolve()
    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        dirs[:] = sorted(
            d for d in dirs
            if d not in EXCLUDED_DIRS and not d.startswith(".")
        )
        for filename in files:
            path = current_path / filename
            if path.resolve() == index_resolved:
                continue
            if path.suffix.lower() not in INCLUDED_SUFFIXES:
                continue
            try:
                if path.is_file() and path.stat().st_size <= MAX_SCAN_BYTES:
                    found.append(path)
            except OSError:
                continue
    return sorted(found)

def detect_signals(path: Path) -> tuple[list[str], list[str]]:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore").lower()
    except (OSError, UnicodeError):
        return [], []
    technologies: list[str] = []
    signals: list[str] = []
    for technology, tokens in SIGNALS.items():
        matched = [token for token in tokens if token in content]
        if matched:
            technologies.append(technology)
            signals.extend(matched[:8])
    suffix = path.suffix.lower()
    if suffix in {".java", ".kt", ".kts", ".groovy"}:
        if "jvm" not in technologies:
            technologies.append("jvm")
    if suffix == ".py":
        technologies.append("python")
    return sorted(set(technologies)), sorted(set(signals))

def load_index(index_path: Path) -> dict[str, Any] | None:
    if not index_path.exists():
        return None
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("files"), dict):
            return None
        return data
    except (OSError, json.JSONDecodeError, UnicodeError):
        return None

def make_entry(path: Path, root: Path, file_hash: str) -> dict[str, Any]:
    stat = path.stat()
    technologies, signals = detect_signals(path)
    return {
        "hash": file_hash,
        "size": stat.st_size,
        "lastModified": datetime.fromtimestamp(
            stat.st_mtime, timezone.utc
        ).isoformat(timespec="seconds"),
        "technologies": technologies,
        "signals": signals,
    }

def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        # Validate before replacing the previous index.
        with open(temp_name, "r", encoding="utf-8") as stream:
            json.load(stream)
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Flex project root")
    parser.add_argument("--index", help="Index JSON path; defaults to <root>/index/project-index.json")
    parser.add_argument("--force", action="store_true", help="Force full rebuild")
    parser.add_argument("--status", action="store_true", help="Show index status without updating")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: project root is not a directory: {root}", file=sys.stderr)
        return 2

    index_path = Path(args.index).expanduser().resolve() if args.index else (root / DEFAULT_INDEX_RELATIVE)
    existing = load_index(index_path)

    if args.status:
        if existing is None:
            print("Index: missing or invalid")
            return 1
        metadata = existing.get("metadata", {})
        print(f"Index: valid\nProject: {metadata.get('project', 'unknown')}")
        print(f"Version: {metadata.get('version', 'unknown')}")
        print(f"Files: {len(existing.get('files', {}))}")
        print(f"Last updated: {metadata.get('lastUpdatedAt', 'unknown')}")
        return 0

    # Full rebuild when forced, absent/invalid, schema incompatible, or scan config changed.
    full_reasons = []
    if args.force:
        full_reasons.append("forced")
    if existing is None:
        full_reasons.append("missing_or_invalid_index")
    else:
        metadata = existing.get("metadata", {})
        if metadata.get("version") != INDEX_VERSION:
            full_reasons.append("index_version_changed")
        if metadata.get("scanConfigVersion") != SCAN_CONFIG_VERSION:
            full_reasons.append("scan_config_changed")
        if metadata.get("projectRoot") != str(root):
            full_reasons.append("project_root_changed")

    mode = "FULL" if full_reasons else "INCREMENTAL"
    old_files = {} if mode == "FULL" else existing.get("files", {})
    new_files: dict[str, Any] = {}
    added = modified = unchanged = 0

    try:
        paths = discover_files(root, index_path)
        for path in paths:
            relative = path.relative_to(root).as_posix()
            current_hash = sha256_file(path)
            previous = old_files.get(relative)
            if previous and previous.get("hash") == current_hash:
                new_files[relative] = previous
                unchanged += 1
            else:
                new_files[relative] = make_entry(path, root, current_hash)
                if previous:
                    modified += 1
                else:
                    added += 1
    except OSError as exc:
        print(f"ERROR: scan failed; previous index was not replaced: {exc}", file=sys.stderr)
        return 3

    deleted = len(set(old_files) - set(new_files))
    metadata = {
        "project": root.name,
        "projectRoot": str(root),
        "version": INDEX_VERSION,
        "scanConfigVersion": SCAN_CONFIG_VERSION,
        "generatedAt": (
            existing.get("metadata", {}).get("generatedAt", utc_now())
            if mode == "INCREMENTAL" and existing else utc_now()
        ),
        "lastUpdatedAt": utc_now(),
        "scanMode": mode.lower(),
        "fullRebuildReasons": full_reasons,
        "fileCount": len(new_files),
    }
    result = {"metadata": metadata, "files": new_files}

    try:
        atomic_write_json(index_path, result)
    except (OSError, TypeError, ValueError) as exc:
        print(f"ERROR: could not safely write index: {exc}", file=sys.stderr)
        return 4

    print("Project Index Result")
    print("--------------------")
    print(f"Mode:             {mode}")
    if full_reasons:
        print(f"Reason:           {', '.join(full_reasons)}")
    print(f"Total files:      {len(new_files)}")
    print(f"New files:        {added}")
    print(f"Modified files:   {modified}")
    print(f"Deleted files:    {deleted}")
    print(f"Unchanged files:  {unchanged}")
    print(f"Index:            {index_path}")
    print("Index updated successfully.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
