from __future__ import annotations

from datetime import date

from src.comitato.comitato_azure_retirements.libs.workflow_exports_grouping import (
    UNKNOWN_PLATFORM,
    aggregate_group,
)
from src.comitato.comitato_azure_retirements.libs.workflow_exports_utils import (
    normalize_key,
)


def test_aggregate_group_builds_platform_map_dates_and_priority() -> None:
    grouped = aggregate_group(
        advisory_key="advisor_retirement|tls-1.0|2026-06-01",
        rows=[
            {
                "source_identifiers": ["id-1"],
                "source_links": ["https://example.com/one"],
                "source_system": "advisor_joined",
                "subscription_name": "PROD-IO",
                "retirement_date": "2026-06-01",
                "retirement_date_quality": "derived",
                "retiring_feature": "TLS 1.0 retirement",
                "summary_text": "TLS 1.0 is deprecated",
                "details_text": "Migrate to TLS 1.2",
                "action_required": "Upgrade TLS settings",
                "technology_or_service": "Azure App Service",
                "advice_type": "advisor_retirement",
                "as_of_date": "2026-05-20",
            },
            {
                "source_identifiers": ["id-2"],
                "source_links": [],
                "source_system": "resource_health_events",
                "subscription_name": "UNMAPPED-SUB",
                "retirement_date": "2026-07-01",
                "retirement_date_quality": "exact",
                "retiring_feature": "TLS 1.0 retirement",
                "summary_text": "Migration required",
                "details_text": "No extra details",
                "action_required": "",
                "technology_or_service": "",
                "advice_type": "advisor_retirement",
                "as_of_date": "2026-05-25",
            },
        ],
        active_platform_map={"prod-io": "IO"},
        normalize_key=normalize_key,
        as_of_date=date(2026, 1, 1),
    )

    assert grouped["impacted_platforms"] == "IO, Unknown Platform"
    assert f'"{UNKNOWN_PLATFORM}":["UNMAPPED-SUB"]' in grouped[
        "impacted_platforms_subscriptions_json"
    ]
    assert grouped["retirement_date"] == "2026-06-01"
    assert grouped["retirement_date_quality"] == "derived"
    assert grouped["priority_label"] == "Prioritario"
    assert grouped["first_seen_date"] == "2026-05-20"
    assert grouped["last_seen_date"] == "2026-05-25"
