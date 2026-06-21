#!/usr/bin/env python3
"""Export Azure retirements into separated Advisor and Service Health aggregate TSV files."""

from __future__ import annotations

import sys
from pathlib import Path

from libs.config import parse_args
from libs.runtime_runner import run_export


def main() -> int:
    cfg = parse_args()
    return run_export(
        cfg=cfg,
        argv=sys.argv,
        script_path=Path(__file__),
    )


if __name__ == "__main__":
    raise SystemExit(main())
