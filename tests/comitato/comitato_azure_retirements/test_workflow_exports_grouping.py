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
                "source": "advisor",
                "source_system": "advisor_joined",
                "subscription_name": "PROD-IO",
                "retirement_date": "2026-06-01",
                "retiring_feature": "TLS 1.0 retirement",
                "summary_text": "TLS 1.0 is deprecated",
                "_descrizione_problema_raw": "TLS 1.0 is deprecated",
                "action_required": "Upgrade TLS settings",
                "technology_or_service": "Azure App Service",
                "advice_type": "advisor_retirement",
                "as_of_date": "2026-05-20",
            },
            {
                "source_identifiers": ["id-2"],
                "source_links": [],
                "source": "advisor",
                "source_system": "advisor_joined",
                "subscription_name": "UNMAPPED-SUB",
                "retirement_date": "2026-07-01",
                "retiring_feature": "TLS 1.0 retirement",
                "summary_text": "Migration required",
                "_descrizione_problema_raw": "No extra details",
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

    assert grouped["source"] == "advisor"
    assert grouped["_descrizione_problema_raw"] == "TLS 1.0 is deprecated"
    assert grouped["impacted_platforms"] == "IO, Unknown Platform"
    assert (
        f'"{UNKNOWN_PLATFORM}":["UNMAPPED-SUB"]'
        in grouped["impacted_platforms_subscriptions_json"]
    )
    assert grouped["retirement_date"] == "2026-06-01"
    assert "retirement_date_quality" not in grouped
    assert "details_text" not in grouped
    assert grouped["priority_label"] == "Prioritario"
    assert grouped["first_seen_date"] == "2026-05-20"
    assert grouped["last_seen_date"] == "2026-05-25"


def test_aggregate_group_falls_back_to_subscription_id_from_source_identifier() -> None:
    grouped = aggregate_group(
        advisory_key="advisor_retirement|sdk|na",
        rows=[
            {
                "source_identifiers": [
                    "/subscriptions/sub-1/resourceGroups/rg/providers/Microsoft.KeyVault/vaults/kv/providers/Microsoft.Advisor/recommendations/rec-1"
                ],
                "source_links": [],
                "source_system": "advisor_joined",
                "subscription_name": "",
                "retirement_date": "",
                "retirement_date_quality": "missing",
                "retiring_feature": "Upgrade SDK",
                "summary_text": "Upgrade SDK",
                "details_text": "",
                "action_required": "Upgrade SDK",
                "technology_or_service": "Key vault",
                "advice_type": "advisor_retirement",
                "as_of_date": "2026-05-20",
            }
        ],
        active_platform_map={},
        normalize_key=normalize_key,
        as_of_date=date(2026, 1, 1),
    )

    assert grouped["impacted_platforms"] == UNKNOWN_PLATFORM
    assert grouped["impacted_subscriptions"] == "sub-1"
    assert (
        grouped["impacted_platforms_subscriptions_json"]
        == '{"platforms":{"Unknown Platform":["sub-1"]}}'
    )
