from __future__ import annotations

from src.comitato.comitato_azure_retirements.libs.normalize_shared import (
    date_from_normalized_datetime,
    extract_retirement_deadline_from_text,
    parse_retirement_date_candidate,
    service_health_date_for_window,
)


def test_parse_retirement_date_candidate_handles_iso_and_human_dates() -> None:
    iso_date, iso_is_derived = parse_retirement_date_candidate("2027-06-30")
    text_date, text_is_derived = parse_retirement_date_candidate("30 June 2027")

    assert iso_date == "2027-06-30"
    assert iso_is_derived is False
    assert text_date == "2027-06-30"
    assert text_is_derived is True


def test_extract_retirement_deadline_from_text_requires_retirement_signal() -> None:
    detected_date, detected_derived = extract_retirement_deadline_from_text(
        title="AKS Ubuntu 22.04 node image will retire on 30 June 2027",
        summary="",
        description="",
        recommended_actions="",
    )
    missing_date, missing_derived = extract_retirement_deadline_from_text(
        title="General update 30 June 2027",
        summary="",
        description="",
        recommended_actions="",
    )

    assert detected_date == "2027-06-30"
    assert detected_derived is True
    assert missing_date == ""
    assert missing_derived is False


def test_service_health_date_for_window_falls_back_to_impact_dates() -> None:
    resolved_date, is_derived = service_health_date_for_window(
        title="Maintenance notice",
        summary="No explicit retirement date in text",
        description="",
        recommended_actions="",
        impact_mitigation="2027-01-15T00:00:00Z",
        impact_start="2026-09-01T00:00:00Z",
        last_update="2026-06-18T12:00:00Z",
    )

    assert resolved_date == "2027-01-15"
    assert is_derived is False


def test_date_from_normalized_datetime_extracts_only_date_portion() -> None:
    assert date_from_normalized_datetime("2026-06-18T12:00:00Z") == "2026-06-18"
    assert date_from_normalized_datetime("") == ""
