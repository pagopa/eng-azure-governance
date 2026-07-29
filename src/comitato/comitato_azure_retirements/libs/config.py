"""Configuration parsing for the Azure retirements exporter."""

from __future__ import annotations

import argparse
import configparser
import os
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Sequence

from .dates import add_calendar_months, parse_iso_date

REL_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "azure_rel.conf"
LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})


@dataclass(frozen=True)
class LoggingSettings:
    enabled: bool = True
    level: str = "INFO"
    console_level: str = "INFO"
    include_traceback: bool = True
    log_directory: Path | None = None


@dataclass(frozen=True)
class RelConfig:
    allowed_regions: frozenset[str]
    logging: LoggingSettings


def _normalized_region(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.strip().lower())


def _configured_log_level(parser: configparser.ConfigParser, option: str) -> str:
    level = parser.get("logging", option).strip().upper()
    if level not in LOG_LEVELS:
        raise ValueError(
            f"logging.{option} must be one of: {', '.join(sorted(LOG_LEVELS))}"
        )
    return level


def load_rel_config(path: Path = REL_CONFIG_PATH) -> RelConfig:
    parser = configparser.ConfigParser(interpolation=None)
    if not path.is_file():
        raise FileNotFoundError(f"Azure retirements configuration not found: {path}")
    parser.read(path, encoding="utf-8")

    missing_sections = [
        section for section in ("regions", "logging") if not parser.has_section(section)
    ]
    if missing_sections:
        raise ValueError(
            f"Missing azure_rel.conf section(s): {', '.join(missing_sections)}"
        )

    raw_regions = parser.get("regions", "allowed", fallback="")
    allowed_regions = frozenset(
        normalized
        for item in raw_regions.replace(",", "\n").splitlines()
        if (normalized := _normalized_region(item))
    )
    if not allowed_regions:
        raise ValueError("regions.allowed must contain at least one Azure region")

    raw_log_directory = parser.get("logging", "log_directory", fallback="").strip()
    log_directory: Path | None = None
    if raw_log_directory:
        candidate = Path(raw_log_directory).expanduser()
        log_directory = (
            candidate if candidate.is_absolute() else path.parent / candidate
        ).resolve()

    return RelConfig(
        allowed_regions=allowed_regions,
        logging=LoggingSettings(
            enabled=parser.getboolean("logging", "enabled"),
            level=_configured_log_level(parser, "level"),
            console_level=_configured_log_level(parser, "console_level"),
            include_traceback=parser.getboolean("logging", "include_traceback"),
            log_directory=log_directory,
        ),
    )


DEFAULT_REL_CONFIG = load_rel_config()


@dataclass(frozen=True)
class RuntimeConfig:
    mode: str
    workflows: list[str]
    subscriptions: list[str]
    management_groups: list[str]
    output_root: Path
    as_of_date: date
    health_query_start: date
    fixture_dir: Path | None
    write_raw_jsonl: bool
    allow_degraded: bool
    verbose: bool
    max_workers: int | None = None
    logging: LoggingSettings = field(default_factory=lambda: DEFAULT_REL_CONFIG.logging)


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    items = [item.strip() for item in value.split(",")]
    return [item for item in items if item]


def _env_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _parse_positive_int(
    raw_value: str | None, *, argument_name: str, parser: argparse.ArgumentParser
) -> int | None:
    if raw_value is None or raw_value == "":
        return None
    try:
        value = int(raw_value)
    except ValueError:
        parser.error(f"{argument_name} must be an integer")
    if value < 1:
        parser.error(f"{argument_name} must be greater than zero")
    return value


def _parse_workflows(
    raw_value: str | None, *, parser: argparse.ArgumentParser
) -> list[str]:
    allowed_workflows = {"raw", "aggregate", "slide", "full"}
    full_workflow = ["raw", "aggregate", "slide"]

    if raw_value is None or raw_value.strip() == "":
        return full_workflow

    requested = [item.strip().lower() for item in raw_value.split(",") if item.strip()]
    if not requested:
        return full_workflow

    unknown = sorted({item for item in requested if item not in allowed_workflows})
    if unknown:
        parser.error(f"--workflow contains unsupported value(s): {', '.join(unknown)}")

    if "full" in requested and len(requested) > 1:
        parser.error("--workflow=full cannot be combined with other workflow values")

    if requested == ["full"]:
        return full_workflow

    selected: list[str] = []
    for workflow in requested:
        if workflow not in selected:
            selected.append(workflow)

    return selected


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="comitato-azure-retirements",
        description="Export Azure Advisor retirements and Service Health advisories into separate TSV files.",
    )
    parser.add_argument(
        "--mode", choices=["live", "schema-only", "fixture"], default=None
    )
    parser.add_argument(
        "--workflow",
        default=None,
        help="Comma-separated workflow list: raw,aggregate,slide or full (default: full)",
    )
    parser.add_argument("--subscriptions", default=None)
    parser.add_argument("--management-groups", default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--as-of-date", default=None)
    parser.add_argument("--health-query-start", default=None)
    parser.add_argument("--fixture-dir", default=None)
    parser.add_argument("--write-raw-jsonl", action="store_true")
    parser.add_argument("--allow-degraded", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--max-workers", type=int, default=None)
    return parser


def parse_args(argv: Sequence[str] | None = None) -> RuntimeConfig:
    parser = build_parser()
    args = parser.parse_args(argv)

    mode = args.mode or os.getenv("AZURE_RETIREMENTS_MODE") or "live"
    workflows = _parse_workflows(
        args.workflow or os.getenv("AZURE_RETIREMENTS_WORKFLOW"), parser=parser
    )

    subscriptions = _split_csv(args.subscriptions or os.getenv("AZURE_SUBSCRIPTIONS"))
    management_groups = _split_csv(
        args.management_groups or os.getenv("AZURE_MANAGEMENT_GROUPS")
    )

    output_root_raw = args.output_root or os.getenv("AZURE_RETIREMENTS_OUTPUT_ROOT")
    if output_root_raw:
        output_root = Path(output_root_raw).expanduser().resolve()
    else:
        output_root = Path(__file__).resolve().parent.parent / "exports"

    as_of_raw = args.as_of_date or os.getenv("AZURE_RETIREMENTS_AS_OF_DATE")
    as_of_date = parse_iso_date(as_of_raw) if as_of_raw else date.today()

    health_query_start_raw = args.health_query_start or os.getenv(
        "AZURE_HEALTH_QUERY_START"
    )
    if health_query_start_raw:
        health_query_start = parse_iso_date(health_query_start_raw)
    else:
        health_query_start = add_calendar_months(as_of_date, -18)

    fixture_dir_raw = args.fixture_dir or os.getenv("AZURE_RETIREMENTS_FIXTURE_DIR")
    fixture_dir = (
        Path(fixture_dir_raw).expanduser().resolve() if fixture_dir_raw else None
    )

    write_raw_jsonl = args.write_raw_jsonl or _env_bool(
        os.getenv("AZURE_RETIREMENTS_WRITE_RAW_JSONL")
    )
    allow_degraded = args.allow_degraded or _env_bool(
        os.getenv("AZURE_RETIREMENTS_ALLOW_DEGRADED")
    )
    verbose = args.verbose or _env_bool(os.getenv("AZURE_RETIREMENTS_VERBOSE"))
    max_workers: int | None
    if args.max_workers is not None:
        max_workers = _parse_positive_int(
            str(args.max_workers), argument_name="--max-workers", parser=parser
        )
    else:
        max_workers = _parse_positive_int(
            os.getenv("AZURE_RETIREMENTS_MAX_WORKERS"),
            argument_name="AZURE_RETIREMENTS_MAX_WORKERS",
            parser=parser,
        )

    if mode == "live" and not subscriptions and not management_groups:
        parser.error("live mode requires --subscriptions or --management-groups")

    if mode == "fixture" and fixture_dir is None:
        parser.error(
            "fixture mode requires --fixture-dir or AZURE_RETIREMENTS_FIXTURE_DIR"
        )

    return RuntimeConfig(
        mode=mode,
        workflows=workflows,
        subscriptions=subscriptions,
        management_groups=management_groups,
        output_root=output_root,
        as_of_date=as_of_date,
        health_query_start=health_query_start,
        fixture_dir=fixture_dir,
        write_raw_jsonl=write_raw_jsonl,
        allow_degraded=allow_degraded,
        verbose=verbose,
        max_workers=max_workers,
        logging=DEFAULT_REL_CONFIG.logging,
    )
