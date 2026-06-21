#!/usr/bin/env python3
"""Export Azure retirements into separated Advisor and Service Health aggregate TSV files."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

from libs.config import RuntimeConfig, parse_args
from libs.runtime_router import RuntimeRoute, build_runtime_route

RunExportFn = Callable[..., int]


def _load_run_export() -> RunExportFn:
    from libs.runtime_runner import run_export

    return run_export


def dispatch_route(
    *,
    cfg: RuntimeConfig,
    route: RuntimeRoute,
    argv: list[str],
    script_path: Path,
    run_export_fn: RunExportFn | None = None,
) -> int:
    if cfg.verbose:
        print(
            f"Runtime route: {route.name} [{route.describe()}]",
            file=sys.stderr,
        )

    selected_runner = run_export_fn or _load_run_export()
    return selected_runner(
        cfg=cfg,
        argv=argv,
        script_path=script_path,
        route=route,
    )


def main() -> int:
    cfg = parse_args()
    route = build_runtime_route(cfg.workflows)
    return dispatch_route(
        cfg=cfg,
        route=route,
        argv=sys.argv,
        script_path=Path(__file__),
    )


if __name__ == "__main__":
    raise SystemExit(main())
