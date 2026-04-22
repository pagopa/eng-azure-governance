#!/usr/bin/env python3
"""Replay registered imported-asset override patches after an upstream refresh."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply registered imported-asset override patches."
    )
    parser.add_argument(
        "--registry",
        help="Path to imported-asset-overrides.yaml.",
    )
    parser.add_argument(
        "--repo-root",
        help="Repository root. Defaults to the nearest parent that contains .github/.",
    )
    parser.add_argument(
        "--id",
        action="append",
        dest="selected_ids",
        help="Apply only the selected override id. Repeatable.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check patch applicability without writing changes.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = (
        find_repo_root(Path(args.repo_root))
        if args.repo_root
        else find_repo_root(Path.cwd())
    )
    skill_root = (
        Path(args.registry).resolve().parent.parent
        if args.registry
        else Path(__file__).resolve().parent.parent
    )
    registry_path = (
        Path(args.registry).resolve()
        if args.registry
        else skill_root / "references/imported-asset-overrides.yaml"
    )
    overrides = load_registry(registry_path)
    selected = select_overrides(overrides, args.selected_ids)
    if not selected:
        print("No imported-asset overrides selected.", file=sys.stderr)
        return 1

    sys.path.insert(0, str((repo_root / ".github/scripts").resolve()))
    from lib.fingerprinting import build_fingerprint  # pylint: disable=import-error

    for override in selected:
        override_id = override["id"]
        patch_path = (skill_root / override["patch_path"]).resolve()
        target_path = repo_root / override["target_path"]
        if not patch_path.is_file():
            print(f"[error] missing patch file for {override_id}: {patch_path}", file=sys.stderr)
            return 1
        if not target_path.is_file():
            print(f"[error] missing target file for {override_id}: {target_path}", file=sys.stderr)
            return 1

        apply_strategy = override.get("apply_strategy", "git-apply")
        patch_status = detect_patch_status(repo_root, patch_path, apply_strategy=apply_strategy)
        if patch_status == "conflict":
            print(
                f"[error] patch does not apply cleanly for {override_id}; stop and review the override.",
                file=sys.stderr,
            )
            return 1

        if args.dry_run:
            if patch_status == "already-applied":
                print(f"[dry-run] {override_id}: patch already applied")
            elif patch_status == "applicable-with-3way":
                print(
                    f"[dry-run] {override_id}: patch needs 3-way replay "
                    f"({apply_strategy}) because upstream text changed"
                )
            else:
                print(f"[dry-run] {override_id}: patch applies cleanly")
            continue

        if patch_status == "already-applied":
            print(f"[skipped] {override_id}: patch already applied")
            continue

        apply_cmd = build_apply_command(patch_path, patch_status)
        if run_git(apply_cmd, repo_root) != 0:
            print(f"[error] failed to apply patch for {override_id}", file=sys.stderr)
            return 1

        expected_hash = override["expected_content_hash"]
        actual_hash = build_fingerprint(repo_root, target_path).content_hash
        if actual_hash != expected_hash:
            print(
                f"[error] patched content hash mismatch for {override_id}: "
                f"expected {expected_hash}, got {actual_hash}",
                file=sys.stderr,
            )
            return 1

        if patch_status == "applicable-with-3way":
            print(f"[applied] {override_id}: {override['target_path']} via 3-way replay")
        else:
            print(f"[applied] {override_id}: {override['target_path']}")

    return 0


def find_repo_root(start: Path) -> Path:
    candidate = start.resolve()
    for current in (candidate, *candidate.parents):
        if (current / ".github").is_dir():
            return current
    raise FileNotFoundError(f"Unable to find repository root from {start}")


def load_registry(path: Path) -> list[dict[str, str]]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    overrides = payload.get("overrides")
    if not isinstance(overrides, list):
        raise ValueError("Registry must define an overrides list.")
    normalized: list[dict[str, str]] = []
    for item in overrides:
        if not isinstance(item, dict):
            raise ValueError("Each override entry must be a mapping.")
        normalized.append({key: str(value) for key, value in item.items()})
    return normalized


def select_overrides(
    overrides: list[dict[str, str]], selected_ids: list[str] | None
) -> list[dict[str, str]]:
    if not selected_ids:
        return overrides
    selected_set = set(selected_ids)
    return [override for override in overrides if override.get("id") in selected_set]


def run_git(command: list[str], repo_root: Path, quiet: bool = False) -> int:
    completed = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if not quiet and completed.stdout.strip():
        print(completed.stdout.strip())
    if not quiet and completed.stderr.strip():
        print(completed.stderr.strip(), file=sys.stderr)
    return completed.returncode


def build_apply_command(patch_path: Path, patch_status: str) -> list[str]:
    command = ["git", "apply"]
    if patch_status == "applicable-with-3way":
        command.append("--3way")
    command.append(patch_path.as_posix())
    return command


def detect_patch_status(
    repo_root: Path,
    patch_path: Path,
    apply_strategy: str = "git-apply",
) -> str:
    if run_git(["git", "apply", "--check", patch_path.as_posix()], repo_root, quiet=True) == 0:
        return "applicable"
    if (
        run_git(
            ["git", "apply", "--reverse", "--check", patch_path.as_posix()],
            repo_root,
            quiet=True,
        )
        == 0
    ):
        return "already-applied"
    if apply_strategy == "git-apply-3way" and (
        run_git(
            ["git", "apply", "--3way", "--check", patch_path.as_posix()],
            repo_root,
            quiet=True,
        )
        == 0
    ):
        return "applicable-with-3way"
    return "conflict"


if __name__ == "__main__":
    raise SystemExit(main())
