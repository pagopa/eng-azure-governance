from __future__ import annotations

from datetime import date

from src.comitato.comitato_azure_retirements.libs.workflow_exports import (
    UNKNOWN_PLATFORM,
    build_aggregate_rows,
    build_slide_rows,
    load_active_subscription_platform_map,
)
from src.comitato.comitato_azure_retirements.libs.schemas import (
    AGGREGATE_HEADERS,
    SLIDE_HEADERS,
)
from src.comitato.comitato_azure_retirements.libs.workflow_exports_utils import (
    PRIORITY_LABEL_RANK,
    priority_label,
)


def test_load_active_subscription_platform_map_uses_active_only(tmp_path) -> None:  # type: ignore[no-untyped-def]
    platforms_file = tmp_path / "platforms.yaml"
    platforms_file.write_text(
        """
IO:
  active:
    - PROD-IO
  disabled:
    - DEV-IO
SelfCare:
  active:
    - PROD-SelfCare
""".strip(),
        encoding="utf-8",
    )

    mapping = load_active_subscription_platform_map(platforms_file)

    assert mapping["prod-io"] == "IO"
    assert mapping["prod-selfcare"] == "SelfCare"
    assert "dev-io" not in mapping


def test_build_aggregate_rows_groups_platforms_and_unknown_bucket() -> None:
    advisor_rows = [
        {
            "retiring_feature": "TLS 1.0 retirement",
            "short_description_solution": "Upgrade TLS",
            "short_description_problem": "TLS 1.0 is deprecated",
            "description": "Use TLS 1.2",
            "retirement_date": "2026-12-31",
            "subscription_name": "PROD-IO",
            "source_system": "advisor_joined",
            "source_id": "source-1",
            "advisor_recommendation_id": "rec-1",
            "action_link": "https://example.com/action",
            "learn_more_link": "https://example.com/learn",
            "as_of_date": "2026-06-19",
        },
        {
            "retiring_feature": "TLS 1.0 retirement",
            "short_description_solution": "Upgrade TLS",
            "short_description_problem": "TLS 1.0 is deprecated",
            "description": "Use TLS 1.2",
            "retirement_date": "2026-12-31",
            "subscription_name": "SUB-NOT-MAPPED",
            "source_system": "advisor_joined",
            "source_id": "source-2",
            "advisor_recommendation_id": "rec-2",
            "action_link": "",
            "learn_more_link": "https://example.com/learn",
            "as_of_date": "2026-06-19",
        },
    ]

    aggregate_rows = build_aggregate_rows(
        advisor_rows=advisor_rows,
        service_rows=[],
        active_platform_map={"prod-io": "IO"},
        as_of_date=date(2026, 6, 19),
    )

    assert len(aggregate_rows) == 1
    row = aggregate_rows[0]
    assert row["advice_type"] == "advisor_retirement"
    assert row["retirement_date"] == "2026-12-31"
    assert row["impacted_platforms"] == "IO, Unknown Platform"
    assert '"IO":["PROD-IO"]' in row["impacted_platforms_subscriptions_json"]
    assert (
        f'"{UNKNOWN_PLATFORM}":["SUB-NOT-MAPPED"]'
        in row["impacted_platforms_subscriptions_json"]
    )


def test_build_aggregate_rows_skips_low_signal_catalog_rows() -> None:
    advisor_rows = [
        {
            "source_system": "advisor_metadata",
            "source_id": "/providers/Microsoft.Advisor/metadata/recommendationImpact",
            "advisor_recommendation_id": "",
            "retiring_feature": "",
            "short_description_problem": "",
            "short_description_solution": "",
            "description": "",
            "service_name": "",
            "retirement_date": "",
            "learn_more_link": "",
            "action_link": "",
            "subscription_name": "",
            "as_of_date": "2026-06-19",
        },
        {
            "retiring_feature": "TLS 1.0 retirement",
            "short_description_solution": "Upgrade TLS",
            "short_description_problem": "TLS 1.0 is deprecated",
            "description": "Use TLS 1.2",
            "retirement_date": "2026-12-31",
            "subscription_name": "PROD-IO",
            "source_system": "advisor_joined",
            "source_id": "source-1",
            "advisor_recommendation_id": "rec-1",
            "action_link": "https://example.com/action",
            "learn_more_link": "https://example.com/learn",
            "service_name": "Azure App Service",
            "as_of_date": "2026-06-19",
        },
    ]

    aggregate_rows = build_aggregate_rows(
        advisor_rows=advisor_rows,
        service_rows=[],
        active_platform_map={"prod-io": "IO"},
        as_of_date=date(2026, 6, 19),
    )

    assert len(aggregate_rows) == 1
    assert aggregate_rows[0]["retiring_feature"] == "TLS 1.0 retirement"
    assert aggregate_rows[0]["source_links"] == "https://example.com/action, https://example.com/learn"


def test_build_aggregate_rows_backfills_source_links_from_advisor_identifiers() -> None:
    advisor_source_id = (
        "/subscriptions/sub-1/resourceGroups/rg-test/providers/Microsoft.Storage/"
        "storageAccounts/storage01/providers/Microsoft.Advisor/recommendations/rec-1"
    )
    advisor_rows = [
        {
            "retiring_feature": "Storage retirement",
            "short_description_solution": "Upgrade storage account",
            "short_description_problem": "Legacy storage account",
            "description": "No URL in this description",
            "retirement_date": "2026-12-31",
            "subscription_name": "PROD-IO",
            "source_system": "advisor_joined",
            "source_id": advisor_source_id,
            "advisor_recommendation_id": advisor_source_id,
            "action_link": "",
            "learn_more_link": "",
            "service_name": "Storage Account",
            "as_of_date": "2026-06-19",
        }
    ]

    aggregate_rows = build_aggregate_rows(
        advisor_rows=advisor_rows,
        service_rows=[],
        active_platform_map={"prod-io": "IO"},
        as_of_date=date(2026, 6, 19),
    )

    assert len(aggregate_rows) == 1
    assert (
        aggregate_rows[0]["source_links"]
        == "https://portal.azure.com/#resource/subscriptions/sub-1/resourceGroups/"
        "rg-test/providers/Microsoft.Storage/storageAccounts/storage01/providers/"
        "Microsoft.Advisor/recommendations/rec-1"
    )


def test_build_aggregate_rows_backfills_blank_subscription_name_from_subscription_id() -> None:
    advisor_rows = [
        {
            "retiring_feature": "Known subscription row",
            "short_description_solution": "Upgrade",
            "short_description_problem": "Known subscription",
            "retirement_date": "2026-12-31",
            "subscription_id": "sub-1",
            "subscription_name": "PROD-IO",
            "source_system": "advisor_joined",
            "source_id": "/subscriptions/sub-1/resourceGroups/rg/providers/Microsoft.Web/sites/app/providers/Microsoft.Advisor/recommendations/known",
            "advisor_recommendation_id": "known",
            "service_name": "App service",
            "as_of_date": "2026-06-19",
        },
        {
            "retiring_feature": "Blank subscription row",
            "short_description_solution": "Upgrade",
            "short_description_problem": "Blank subscription",
            "retirement_date": "2027-01-31",
            "subscription_id": "sub-1",
            "subscription_name": "",
            "source_system": "advisor_joined",
            "source_id": "/subscriptions/sub-1/resourceGroups/rg/providers/Microsoft.KeyVault/vaults/kv/providers/Microsoft.Advisor/recommendations/blank",
            "advisor_recommendation_id": "blank",
            "service_name": "Key vault",
            "as_of_date": "2026-06-19",
        },
    ]

    aggregate_rows = build_aggregate_rows(
        advisor_rows=advisor_rows,
        service_rows=[],
        active_platform_map={"prod-io": "IO"},
        as_of_date=date(2026, 6, 19),
    )

    blank_row = next(
        row for row in aggregate_rows if row["retiring_feature"] == "Blank subscription row"
    )
    assert blank_row["impacted_platforms"] == "IO"
    assert blank_row["impacted_subscriptions"] == "PROD-IO"
    assert blank_row["impacted_platforms_subscriptions_json"] == '{"platforms":{"IO":["PROD-IO"]}}'


def test_build_aggregate_rows_backfills_source_links_from_service_health_identifiers() -> None:
    source_identifier = "Microsoft.ResourceHealth/events/ABCD-123"
    service_rows = [
        {
            "title": "Service retirement notice",
            "summary": "No link in summary",
            "recommended_actions": "Contact operations team",
            "description": "No explicit URL is present",
            "subscription_name": "PROD-IO",
            "source_system": "resource_health_events",
            "source_id": source_identifier,
            "event_id": source_identifier,
            "tracking_id": source_identifier,
            "as_of_date": "2026-06-19",
        }
    ]

    aggregate_rows = build_aggregate_rows(
        advisor_rows=[],
        service_rows=service_rows,
        active_platform_map={"prod-io": "IO"},
        as_of_date=date(2026, 6, 19),
    )

    assert len(aggregate_rows) == 1
    assert (
        aggregate_rows[0]["source_links"]
        == "https://portal.azure.com/#search/Microsoft.ResourceHealth%2Fevents%2FABCD-123"
    )


def test_build_slide_rows_projects_expected_fields() -> None:
    slide_rows = build_slide_rows(
        [
            {
                "impacted_platforms": "IO",
                "impacted_platforms_subscriptions_json": '{"platforms":{"IO":["PROD-IO"]}}',
                "priority_label": "Prioritario",
                "advice_type": "advisor_retirement",
                "technology_or_service": "Azure Cache for Redis",
                "retiring_feature": "Redis version upgrade",
                "action_required": (
                    "<p><strong>Upgrade</strong> to latest supported version</p>"
                ),
                "retirement_date": "2026-10-01",
                "source_links": "https://example.com/redis",
                "summary_text": "Fallback summary",
            }
        ]
    )

    assert slide_rows == [
        {
            "technology_or_service": "Azure Cache for Redis",
            "retiring_feature": "Redis version upgrade",
            "platforms": "IO",
            "platforms_subscriptions_json": '{"platforms":{"IO":["PROD-IO"]}}',
            "priority_label": "Prioritario",
            "advice_type": "advisor_retirement",
            "action_required": "Upgrade to latest supported version",
            "retirement_date": "2026-10-01",
            "source_links": "https://example.com/redis",
        }
    ]


def test_build_slide_rows_backfills_source_links_from_source_identifiers() -> None:
    source_identifier = (
        "/subscriptions/sub-1/resourceGroups/rg-test/providers/Microsoft.KeyVault/"
        "vaults/kv-test/providers/Microsoft.Advisor/recommendations/rec-1"
    )

    slide_rows = build_slide_rows(
        [
            {
                "impacted_platforms": "IO",
                "impacted_platforms_subscriptions_json": '{"platforms":{"IO":["PROD-IO"]}}',
                "priority_label": "Debito",
                "advice_type": "advisor_retirement",
                "technology_or_service": "Azure Key Vault",
                "retiring_feature": "Upgrade SDK",
                "action_required": "Upgrade to latest SDK",
                "retirement_date": "",
                "source_links": "",
                "source_identifiers": source_identifier,
            }
        ]
    )

    assert slide_rows[0]["source_links"] == (
        "https://portal.azure.com/#resource/subscriptions/sub-1/resourceGroups/"
        "rg-test/providers/Microsoft.KeyVault/vaults/kv-test/providers/"
        "Microsoft.Advisor/recommendations/rec-1"
    )


def test_build_slide_rows_uses_summary_fallback_and_strips_xml_tags() -> None:
    slide_rows = build_slide_rows(
        [
            {
                "impacted_platforms": "IO",
                "impacted_platforms_subscriptions_json": '{"platforms":{"IO":["PROD-IO"]}}',
                "priority_label": "Prioritario",
                "advice_type": "service_health_retirement",
                "technology_or_service": "Azure Storage",
                "retiring_feature": "TLS 1.2 migration",
                "action_required": "",
                "summary_text": "<p>Move to <em>TLS 1.2</em>&nbsp;now</p>",
                "retirement_date": "2026-12-01",
                "source_links": "https://example.com/storage",
            }
        ]
    )

    assert slide_rows[0]["action_required"] == "Move to TLS 1.2 now"


def test_headers_follow_requested_committee_contract() -> None:
    assert AGGREGATE_HEADERS[:3] == [
        "impacted_platforms",
        "impacted_subscriptions",
        "impacted_platforms_subscriptions_json",
    ]
    assert AGGREGATE_HEADERS[3:6] == [
        "advice_type",
        "advisory_key",
        "technology_or_service",
    ]
    assert AGGREGATE_HEADERS[6] == "retiring_feature"

    assert SLIDE_HEADERS[:2] == [
        "technology_or_service",
        "retiring_feature",
    ]
    assert SLIDE_HEADERS[2:6] == [
        "platforms",
        "platforms_subscriptions_json",
        "priority_label",
        "advice_type",
    ]
    assert SLIDE_HEADERS[6] == "action_required"


def test_priority_label_producer_values_are_ranked() -> None:
    labels = {
        priority_label(retirement_date="", as_of_date=date(2026, 6, 19)),
        priority_label(retirement_date="2026-07-01", as_of_date=date(2026, 6, 19)),
        priority_label(retirement_date="2026-12-01", as_of_date=date(2026, 6, 19)),
        priority_label(retirement_date="2027-03-01", as_of_date=date(2026, 6, 19)),
        priority_label(retirement_date="2028-06-01", as_of_date=date(2026, 6, 19)),
    }

    assert labels.issubset(set(PRIORITY_LABEL_RANK.keys()))
