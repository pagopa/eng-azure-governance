from __future__ import annotations

from datetime import date

from src.comitato.comitato_azure_retirements.libs.workflow_exports import (
    UNKNOWN_PLATFORM,
    build_aggregate_rows,
    build_slide_rows,
    load_active_subscription_platform_map,
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


def test_build_slide_rows_projects_expected_fields() -> None:
    slide_rows = build_slide_rows(
        [
            {
                "priority_label": "Prioritario",
                "retiring_feature": "Redis version upgrade",
                "action_required": "Upgrade to latest supported version",
                "retirement_date": "2026-10-01",
                "impacted_platforms": "IO",
                "impacted_platforms_subscriptions_json": '{"platforms":{"IO":["PROD-IO"]}}',
                "advice_type": "advisor_retirement",
                "source_links": "https://example.com/redis",
                "summary_text": "Fallback summary",
            }
        ]
    )

    assert slide_rows == [
        {
            "priority_label": "Prioritario",
            "retiring_feature": "Redis version upgrade",
            "action_required": "Upgrade to latest supported version",
            "retirement_date": "2026-10-01",
            "platforms": "IO",
            "platforms_subscriptions_json": '{"platforms":{"IO":["PROD-IO"]}}',
            "advice_type": "advisor_retirement",
            "source_links": "https://example.com/redis",
        }
    ]
