from __future__ import annotations

from datetime import date

from src.comitato.comitato_azure_retirements.libs.workflow_exports_records import (
    advisor_records,
    classify_service_health_type,
    normalize_retirement_date,
    select_publication_records,
    service_health_records,
)


def test_select_publication_records_uses_inclusive_one_year_window() -> None:
    records = [
        {"source_system": "advisor_joined", "platform_state": "New", "publication_date": "2026-07-28", "source_identifiers": ["lower"]},
        {"source_system": "advisor_joined", "platform_state": "New", "publication_date": "2027-07-28", "source_identifiers": ["upper"]},
        {"source_system": "advisor_joined", "platform_state": "New", "publication_date": "2026-07-27", "source_identifiers": ["expired"]},
        {"source_system": "advisor_joined", "platform_state": "New", "publication_date": "2027-07-29", "source_identifiers": ["future"]},
        {"source_system": "advisor_joined", "platform_state": "New", "publication_date": "not-a-date", "source_identifiers": ["invalid"]},
    ]

    selection = select_publication_records(records, as_of_date=date(2026, 7, 28))

    assert [record["source_identifiers"] for record in selection.records] == [["lower"], ["upper"]]
    assert selection.excluded_by_reason == {
        "expired": ["expired"],
        "beyond_one_year": ["future"],
        "missing_or_invalid_date": ["invalid"],
    }


def test_select_publication_records_excludes_non_current_advisor_rows() -> None:
    selection = select_publication_records(
        [
            {"source_system": "advisor_joined", "platform_state": "New", "publication_date": "2026-09-30", "source_identifiers": ["current"]},
            {"source_system": "advisor_joined", "platform_state": "", "publication_date": "2026-09-30", "source_identifiers": ["recommendation-only"]},
        ],
        as_of_date=date(2026, 7, 28),
    )

    assert [record["source_identifiers"] for record in selection.records] == [["current"]]
    assert selection.excluded_by_reason["advisor_not_current"] == ["recommendation-only"]


def test_service_health_publication_selection_uses_impact_mitigation_time() -> None:
    records = service_health_records(
        [
            {
                "source_id": "future-event",
                "tracking_id": "future-event",
                "impact_mitigation_time": "2027-07-29T00:00:00Z",
                "date_for_window": "2026-09-30",
                "title": "Service retirement notice",
                "event_sub_type": "Retirement",
            }
        ]
    )

    selection = select_publication_records(records, as_of_date=date(2026, 7, 28))

    assert selection.records == []
    assert selection.excluded_by_reason["beyond_one_year"] == ["future-event"]


def test_classify_service_health_type_prioritizes_deprecation_then_retirement() -> None:
    assert (
        classify_service_health_type(
            title="Deprecated API",
            summary="",
            description="",
            event_sub_type="Retirement",
        )
        == "service_health_deprecation"
    )
    assert (
        classify_service_health_type(
            title="Maintenance notice",
            summary="",
            description="",
            event_sub_type="Retirement",
        )
        == "service_health_retirement"
    )
    assert (
        classify_service_health_type(
            title="Maintenance notice",
            summary="",
            description="",
            event_sub_type="Informational",
        )
        == "other_advisory"
    )


def test_normalize_retirement_date_supports_explicit_and_text_dates() -> None:
    explicit_date, explicit_quality, explicit_from_text = normalize_retirement_date(
        explicit_date="2027-06-30",
        source_texts=[],
        exact_quality=True,
    )
    text_date, text_quality, text_from_text = normalize_retirement_date(
        explicit_date="",
        source_texts=["AKS node image will retire on 30 June 2027"],
        exact_quality=True,
    )

    assert explicit_date == "2027-06-30"
    assert explicit_quality == "exact"
    assert explicit_from_text is False
    assert text_date == "2027-06-30"
    assert text_quality == "derived"
    assert text_from_text is True


def test_advisor_records_skip_low_signal_metadata_rows() -> None:
    rows = advisor_records(
        [
            {
                "source_system": "advisor_metadata",
                "source_id": "",
                "advisor_recommendation_id": "",
                "retiring_feature": "",
                "short_description_problem": "",
                "short_description_solution": "",
                "description": "",
                "service_name": "",
                "retirement_date": "",
                "action_link": "",
                "learn_more_link": "",
            }
        ]
    )

    assert rows == []


def test_advisor_records_use_approved_raw_lineage() -> None:
    rows = advisor_records(
        [{
            "service_name": "Azure Key Vault",
            "retiring_feature": "Legacy API",
            "short_description_problem": "Legacy API is retiring",
            "short_description_solution": "Move to the supported API",
            "description": "Do not use this inferred description",
            "retirement_date": "2027-02-27",
            "learn_more_link": "https://example.com/learn",
            "action_link": "https://example.com/action-must-not-be-exported",
            "source_system": "advisor_joined",
            "source_id": "advisor-source",
            "advisor_recommendation_id": "advisor-rec",
            "platform_state": "New",
            "as_of_date": "2026-07-28",
        }]
    )

    assert rows[0]["source"] == "advisor"
    assert rows[0]["technology_or_service"] == "Azure Key Vault"
    assert rows[0]["_descrizione_problema_raw"] == "Legacy API is retiring"
    assert rows[0]["retiring_feature"] == "Legacy API"
    assert rows[0]["action_required"] == "Move to the supported API"
    assert rows[0]["retirement_date"] == "2027-02-27"
    assert rows[0]["source_links"] == ["https://example.com/learn"]
    assert rows[0]["summary_text"] == "Legacy API is retiring"
    assert "retirement_date_quality" not in rows[0]
    assert "details_text" not in rows[0]


def test_service_health_records_use_approved_raw_lineage() -> None:
    rows = service_health_records(
        [{
            "impacted_service": "Azure Monitor",
            "title": "Legacy authentication retirement",
            "short_description_solution": "Migrate to managed identity",
            "recommended_actions": "Lower-priority action",
            "summary": "Subscription impact summary https://example.com/summary",
            "description_problem": "Raw problem https://example.com/problem",
            "date_for_window": "2026-09-30",
            "impact_mitigation_time": "2026-09-30T00:00:00Z",
            "source_system": "resource_health_events",
            "source_id": "health-source",
            "event_id": "health-event",
            "tracking_id": "health-track",
            "event_sub_type": "Retirement",
            "as_of_date": "2026-07-28",
        }]
    )

    assert rows[0]["source"] == "service-health"
    assert rows[0]["technology_or_service"] == "Azure Monitor"
    assert rows[0]["_descrizione_problema_raw"].startswith("Raw problem")
    assert rows[0]["retiring_feature"] == "Legacy authentication retirement"
    assert rows[0]["action_required"] == "Migrate to managed identity"
    assert rows[0]["retirement_date"] == "2026-09-30"
    assert rows[0]["source_links"] == [
        "https://example.com/problem",
        "https://example.com/summary",
    ]
    assert rows[0]["summary_text"].startswith("Subscription impact summary")
    assert "retirement_date_quality" not in rows[0]
    assert "details_text" not in rows[0]


def test_service_health_records_do_not_synthesize_source_links() -> None:
    rows = service_health_records(
        [
            {
                "source_id": "Microsoft.ResourceHealth/events/ABCD-123",
                "event_id": "Microsoft.ResourceHealth/events/ABCD-123",
                "tracking_id": "TRK-1",
                "title": "Service retirement advisory",
                "summary": "No explicit links are provided",
                "recommended_actions": "Review migration guidance",
                "description_problem": "No URLs here",
                "event_sub_type": "Retirement",
                "as_of_date": "2026-06-21",
            }
        ]
    )

    assert len(rows) == 1
    assert rows[0]["source_links"] == []


def test_service_health_records_reads_legacy_description_at_boundary() -> None:
    rows = service_health_records(
        [
            {
                "source_id": "event-1",
                "tracking_id": "TRK-1",
                "title": "Service retirement advisory",
                "description": "Legacy migration guidance",
                "event_sub_type": "Retirement",
            }
        ]
    )

    assert rows[0]["_descrizione_problema_raw"] == "Legacy migration guidance"
    assert rows[0]["action_required"] == ""
