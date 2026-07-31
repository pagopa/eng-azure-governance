"""Immutable, validated process configuration for the v2 live runner."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from collections.abc import Callable, Sequence

from .domain.execution import ReportSelector, RunRequest


_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_CATALOG_PATH = _REPOSITORY_ROOT / "src" / "_source_of_truth" / "eng-finops-platforms.yaml"
_DEFAULT_OUTPUT_PATH = _REPOSITORY_ROOT / "src" / "comitato" / "comitato_azure_retirements_v2" / "exports"


@dataclass(frozen=True, slots=True)
class HttpPolicy:
    timeout_seconds: float = 60.0
    retry_attempts: int = 3
    backoff_seconds: float = 1.0

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("HTTP timeout must be positive")
        if self.retry_attempts < 0:
            raise ValueError("HTTP retry attempts cannot be negative")
        if self.backoff_seconds < 0:
            raise ValueError("HTTP backoff cannot be negative")


@dataclass(frozen=True, slots=True)
class AzureApiVersions:
    advisor: str = "2025-01-01"
    resource_health: str = "2025-05-01"
    resource_graph: str = "2024-04-01"
    subscriptions: str = "2022-12-01"


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    request: RunRequest
    catalog_path: Path = _DEFAULT_CATALOG_PATH
    output_path: Path = _DEFAULT_OUTPUT_PATH
    management_groups: tuple[str, ...] = ()
    http: HttpPolicy = HttpPolicy()
    api_versions: AzureApiVersions = AzureApiVersions()

    @property
    def selector(self) -> ReportSelector:
        return self.request.selector

    @property
    def as_of_date(self) -> date:
        if self.request.as_of_date is None:
            raise RuntimeError("RuntimeConfig requires an as-of date")
        return self.request.as_of_date

    @classmethod
    def from_request(
        cls,
        request: RunRequest,
        *,
        catalog_path: Path | None = None,
        output_path: Path | None = None,
        management_groups: tuple[str, ...] = (),
        today: Callable[[], date] = date.today,
    ) -> "RuntimeConfig":
        resolved_request = request
        if resolved_request.as_of_date is None:
            resolved_request = RunRequest(
                selector=resolved_request.selector,
                subscription_ids=resolved_request.subscription_ids,
                as_of_date=today(),
            )
        return cls(
            request=resolved_request,
            catalog_path=catalog_path or _DEFAULT_CATALOG_PATH,
            output_path=output_path or _DEFAULT_OUTPUT_PATH,
            management_groups=management_groups,
        )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="comitato-azure-retirements-v2",
        description="Acquire and publish live Azure retirement reports.",
    )
    parser.add_argument("--report", choices=tuple(item.value for item in ReportSelector), default="all")
    parser.add_argument("--as-of-date", type=_iso_date, default=None)
    parser.add_argument("--subscriptions", default=None, help="Comma-separated subscription IDs")
    parser.add_argument("--subscription", action="append", default=[], dest="subscription_values")
    parser.add_argument("--management-groups", default=None, help="Comma-separated management group IDs")
    parser.add_argument("--catalog-path", "--catalog", dest="catalog_path", default=None)
    parser.add_argument("--output-path", "--output-root", dest="output_path", default=None)
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument("--retry-attempts", type=int, default=3)
    return parser


def _iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an ISO date (YYYY-MM-DD)") from exc


def _csv_values(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _parse_namespace(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = _parser()
    args = parser.parse_args(argv)
    subscriptions = list(_csv_values(args.subscriptions))
    for value in args.subscription_values:
        subscriptions.extend(_csv_values(value))
    management_groups = _csv_values(args.management_groups)
    if args.management_groups and subscriptions:
        parser.error("--subscriptions/--subscription cannot be combined with --management-groups")
    args.subscription_ids = tuple(sorted(set(subscriptions)))
    args.management_group_ids = tuple(sorted(set(management_groups)))
    return args


def _config_from_namespace(
    args: argparse.Namespace,
    *,
    today: Callable[[], date],
) -> RuntimeConfig:
    request = RunRequest(
        selector=ReportSelector(args.report),
        subscription_ids=args.subscription_ids,
        as_of_date=args.as_of_date or today(),
    )
    return RuntimeConfig(
        request=request,
        catalog_path=Path(
            args.catalog_path
            or os.getenv(
                "COMITATO_AZURE_RETIREMENTS_CATALOG",
                str(_DEFAULT_CATALOG_PATH),
            )
        ),
        output_path=Path(
            args.output_path
            or os.getenv("COMITATO_AZURE_RETIREMENTS_OUTPUT", str(_DEFAULT_OUTPUT_PATH))
        ),
        management_groups=args.management_group_ids,
        http=HttpPolicy(args.timeout_seconds, args.retry_attempts),
    )


def parse_config(
    argv: Sequence[str] | None = None,
    *,
    today: Callable[[], date] = date.today,
) -> RuntimeConfig:
    return _config_from_namespace(_parse_namespace(argv), today=today)


def parse_run_request(argv: Sequence[str] | None = None) -> RunRequest:
    return parse_config(argv).request


__all__ = ["AzureApiVersions", "HttpPolicy", "RuntimeConfig", "parse_config", "parse_run_request"]
