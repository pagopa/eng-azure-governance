from datetime import date
from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements_v2.config import (
    RuntimeConfig,
    parse_config,
    parse_run_request,
)
from src.comitato.comitato_azure_retirements_v2.domain.execution import ReportSelector


def test_defaults_to_all_and_uses_an_iso_as_of_date() -> None:
    request = parse_run_request(["--as-of-date", "2026-07-31"])

    assert request.selector is ReportSelector.ALL
    assert request.as_of_date == date(2026, 7, 31)


def test_defaults_to_repository_source_of_truth_paths() -> None:
    config = parse_config([])
    repository_root = Path(__file__).parents[3]

    assert config.catalog_path == repository_root / "src/_source_of_truth/eng-finops-platforms.yaml"
    assert config.output_path == repository_root / "src/comitato/comitato_azure_retirements_v2/exports"


@pytest.mark.parametrize("selector", tuple(item.value for item in ReportSelector))
def test_accepts_every_report_selector(selector: str) -> None:
    request = parse_run_request(["--report", selector])

    assert request.selector.value == selector


def test_accepts_scope_catalog_and_output_inputs(tmp_path: Path) -> None:
    config = parse_config(
        [
            "--report",
            "advisor",
            "--subscriptions",
            "sub-b,sub-a,sub-b",
            "--catalog-path",
            str(tmp_path / "catalog.yaml"),
            "--output-path",
            str(tmp_path / "published"),
        ]
    )

    assert config.request.selector is ReportSelector.ADVISOR
    assert config.request.subscription_ids == ("sub-a", "sub-b")
    assert config.catalog_path == tmp_path / "catalog.yaml"
    assert config.output_path == tmp_path / "published"
    assert not hasattr(config, "token")


def test_request_parser_is_projection_of_runtime_parser(tmp_path: Path) -> None:
    argv = [
        "--report",
        "advisor",
        "--subscriptions",
        "sub-b,sub-a",
        "--catalog-path",
        str(tmp_path / "catalog.yaml"),
    ]

    assert parse_run_request(argv) == parse_config(argv).request


def test_runtime_config_resolves_date_from_injected_today() -> None:
    config = parse_config([], today=lambda: date(2026, 7, 31))

    assert config.as_of_date == date(2026, 7, 31)


def test_rejects_invalid_date_and_unknown_options() -> None:
    with pytest.raises(SystemExit):
        parse_run_request(["--as-of-date", "31-07-2026"])
    with pytest.raises(SystemExit):
        parse_run_request(["--not-a-real-option"])


def test_rejects_conflicting_scope_inputs() -> None:
    with pytest.raises(SystemExit):
        parse_config(["--subscriptions", "sub-a", "--management-groups", "mg-a"])


def test_runtime_config_is_immutable_and_has_central_http_policy() -> None:
    config = RuntimeConfig.from_request(parse_run_request([]))

    assert config.http.timeout_seconds > 0
    assert config.http.retry_attempts >= 0
    with pytest.raises(AttributeError):
        config.output_path = Path("other")  # type: ignore[misc]


def test_logging_defaults_keep_direct_module_machine_safe() -> None:
    config = parse_config(["--subscriptions", "sub-1"])

    assert config.logging.output_format == "json"
    assert config.logging.debug_log_enabled is True
    assert config.logging.log_level == "INFO"
    assert config.logging.console_level == "INFO"
    assert config.logging.include_traceback is True
    assert config.logging.log_directory is None


def test_logging_flags_override_defaults(tmp_path: Path) -> None:
    config = parse_config(
        [
            "--subscriptions",
            "sub-1",
            "--output-format",
            "human",
            "--verbose",
            "--log-level",
            "DEBUG",
            "--console-level",
            "WARNING",
            "--no-debug-log",
            "--log-directory",
            str(tmp_path),
        ]
    )

    assert config.logging.output_format == "human"
    assert config.logging.verbose is True
    assert config.logging.log_level == "DEBUG"
    assert config.logging.console_level == "WARNING"
    assert config.logging.debug_log_enabled is False
    assert config.logging.log_directory == tmp_path


def test_logging_parser_accepts_human_and_rejects_invalid_levels() -> None:
    assert parse_config(["--output-format=human"]).logging.output_format == "human"

    with pytest.raises(SystemExit):
        parse_config(["--log-level", "TRACE"])

    with pytest.raises(SystemExit):
        parse_config(["--console-level", "TRACE"])
