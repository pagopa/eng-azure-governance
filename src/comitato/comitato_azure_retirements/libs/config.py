"""Configuration parsing for the Azure retirements exporter."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Sequence

from .dates import add_calendar_months, parse_iso_date


@dataclass(frozen=True)
class RuntimeConfig:
    mode: str
    subscriptions: list[str]
    management_groups: list[str]
    output_root: Path
    as_of_date: date
    health_query_start: date
    fixture_dir: Path | None
    write_raw_jsonl: bool
    allow_degraded: bool
    verbose: bool


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    items = [item.strip() for item in value.split(",")]
    return [item for item in items if item]


def _env_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="comitato-azure-retirements",
        description="Export Azure Advisor retirements and Service Health advisories into separate TSV files.",
    )
    parser.add_argument("--mode", choices=["live", "schema-only", "fixture"], default=None)
    parser.add_argument("--subscriptions", default=None)
    parser.add_argument("--management-groups", default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--as-of-date", default=None)
    parser.add_argument("--health-query-start", default=None)
    parser.add_argument("--fixture-dir", default=None)
    parser.add_argument("--write-raw-jsonl", action="store_true")
    parser.add_argument("--allow-degraded", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    return parser


def parse_args(argv: Sequence[str] | None = None) -> RuntimeConfig:
    parser = build_parser()
    args = parser.parse_args(argv)

    mode = args.mode or os.getenv("AZURE_RETIREMENTS_MODE") or "live"

    subscriptions = _split_csv(args.subscriptions or os.getenv("AZURE_SUBSCRIPTIONS"))
    management_groups = _split_csv(args.management_groups or os.getenv("AZURE_MANAGEMENT_GROUPS"))

    output_root_raw = args.output_root or os.getenv("AZURE_RETIREMENTS_OUTPUT_ROOT")
    if output_root_raw:
        output_root = Path(output_root_raw).expanduser().resolve()
    else:
        output_root = Path(__file__).resolve().parent.parent / "exports"

    as_of_raw = args.as_of_date or os.getenv("AZURE_RETIREMENTS_AS_OF_DATE")
    as_of_date = parse_iso_date(as_of_raw) if as_of_raw else date.today()

    health_query_start_raw = args.health_query_start or os.getenv("AZURE_HEALTH_QUERY_START")
    if health_query_start_raw:
        health_query_start = parse_iso_date(health_query_start_raw)
    else:
        health_query_start = add_calendar_months(as_of_date, -18)

    fixture_dir_raw = args.fixture_dir or os.getenv("AZURE_RETIREMENTS_FIXTURE_DIR")
    fixture_dir = Path(fixture_dir_raw).expanduser().resolve() if fixture_dir_raw else None

    write_raw_jsonl = args.write_raw_jsonl or _env_bool(os.getenv("AZURE_RETIREMENTS_WRITE_RAW_JSONL"))
    allow_degraded = args.allow_degraded or _env_bool(os.getenv("AZURE_RETIREMENTS_ALLOW_DEGRADED"))
    verbose = args.verbose or _env_bool(os.getenv("AZURE_RETIREMENTS_VERBOSE"))

    if mode == "live" and not subscriptions and not management_groups:
        parser.error("live mode requires --subscriptions or --management-groups")

    if mode == "fixture" and fixture_dir is None:
        parser.error("fixture mode requires --fixture-dir or AZURE_RETIREMENTS_FIXTURE_DIR")

    return RuntimeConfig(
        mode=mode,
        subscriptions=subscriptions,
        management_groups=management_groups,
        output_root=output_root,
        as_of_date=as_of_date,
        health_query_start=health_query_start,
        fixture_dir=fixture_dir,
        write_raw_jsonl=write_raw_jsonl,
        allow_degraded=allow_degraded,
        verbose=verbose,
    )
