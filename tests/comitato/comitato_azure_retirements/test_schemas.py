from __future__ import annotations

from src.comitato.comitato_azure_retirements.libs.schemas import (
    ADVISOR_HEADERS,
    AGGREGATE_HEADERS,
    DIAGNOSTICS_HEADERS,
    SERVICE_HEALTH_HEADERS,
    SLIDE_HEADERS,
)
from src.comitato.comitato_azure_retirements.libs.workflow_exports import (
    SERVICE_HEALTH_SUPPLEMENTAL_FILENAME,
)


def _assert_unique_non_empty_headers(headers: list[str]) -> None:
    assert headers
    assert len(headers) == len(set(headers))


def test_schema_headers_are_non_empty_and_unique() -> None:
    _assert_unique_non_empty_headers(ADVISOR_HEADERS)
    _assert_unique_non_empty_headers(SERVICE_HEALTH_HEADERS)
    _assert_unique_non_empty_headers(DIAGNOSTICS_HEADERS)
    _assert_unique_non_empty_headers(AGGREGATE_HEADERS)
    _assert_unique_non_empty_headers(SLIDE_HEADERS)


def test_schema_headers_expose_core_contract_fields() -> None:
    assert "run_id" in ADVISOR_HEADERS
    assert "run_id" in SERVICE_HEALTH_HEADERS
    assert "check_id" in DIAGNOSTICS_HEADERS
    assert "advisory_key" in AGGREGATE_HEADERS
    assert "source_links" in SLIDE_HEADERS
    assert SERVICE_HEALTH_SUPPLEMENTAL_FILENAME == "02_azure_service_health_supplemental.tsv"


def test_raw_headers_start_with_canonical_service_health_contract() -> None:
    assert ADVISOR_HEADERS[:2] == ["service_name", "retiring_feature"]
    assert SERVICE_HEALTH_HEADERS[:4] == [
        "tracking_id",
        "short_description_solution",
        "summary",
        "description_problem",
    ]
    assert "description" not in SERVICE_HEALTH_HEADERS
    assert ADVISOR_HEADERS.index("description") == (
        ADVISOR_HEADERS.index("short_description_problem") + 1
    )
