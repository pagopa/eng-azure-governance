#!/usr/bin/env python3
"""Build and diff deterministic resource fingerprints for sync workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPTS_ROOT = REPO_ROOT / ".github/scripts"
DEFAULT_SNAPSHOT_OUTPUT = REPO_ROOT / "tmp/superpowers/internal-agent-sync-control-center.manifest.json"
if SCRIPTS_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, SCRIPTS_ROOT.as_posix())

from lib.fingerprinting import build_manifest, collect_files, diff_manifests, load_manifest, render_diff_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot = subparsers.add_parser("snapshot", help="Generate a fingerprint manifest for files or directories.")
    snapshot.add_argument("paths", nargs="+", help="Files or directories to fingerprint.")
    snapshot.add_argument("--root", default=".", help="Repository root used for relative paths.")
    snapshot.add_argument(
        "--output",
        default=DEFAULT_SNAPSHOT_OUTPUT.as_posix(),
        help="Path to write the JSON manifest. Defaults to tmp/superpowers/internal-agent-sync-control-center.manifest.json.",
    )
    snapshot.add_argument("--source-ref-base", help="Optional prefix used to build source_ref values from relative paths.")

    diff = subparsers.add_parser("diff", help="Compare two fingerprint manifests.")
    diff.add_argument("--old", required=True, help="Baseline manifest path.")
    diff.add_argument("--new", required=True, help="Candidate manifest path.")
    diff.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "snapshot":
        return run_snapshot(args)
    return run_diff(args)


def run_snapshot(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    files = collect_files(root, [Path(path) for path in args.paths])
    manifest = build_manifest(root, files, source_ref_base=args.source_ref_base)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output_path.as_posix())
    return 0


def run_diff(args: argparse.Namespace) -> int:
    old_manifest = load_manifest(Path(args.old))
    new_manifest = load_manifest(Path(args.new))
    result = diff_manifests(old_manifest, new_manifest)
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    print(render_diff_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
