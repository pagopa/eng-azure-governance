from __future__ import annotations

from datetime import date

from src.comitato.comitato_azure_retirements.libs.workflow_exports_utils import (
    build_advisory_key,
    normalize_key,
    portal_link_from_identifier,
    priority_label,
)


def test_normalize_key_collapses_whitespace_and_case() -> None:
    assert normalize_key("  PROD-IO   MAIN  ") == "prod-io main"


def test_build_advisory_key_uses_identifier_digest_when_title_missing() -> None:
    key = build_advisory_key(
        advice_type="advisor_retirement",
        canonical_title_value="",
        canonical_date="na",
        source_identifiers=["id-1", "id-2"],
    )

    assert key.startswith("advisor_retirement||na|")
    assert len(key.split("|", maxsplit=3)[-1]) == 12


def test_portal_link_from_identifier_handles_resource_ids_and_urls() -> None:
    assert portal_link_from_identifier("https://example.com/doc") == "https://example.com/doc"
    assert portal_link_from_identifier("/subscriptions/sub-1/resourceGroups/rg-1") == (
        "https://portal.azure.com/#resource/subscriptions/sub-1/resourceGroups/rg-1"
    )


def test_priority_label_respects_deadline_windows() -> None:
    as_of_date = date(2026, 1, 1)

    assert priority_label(retirement_date="2026-03-15", as_of_date=as_of_date) == "Critico"
    assert priority_label(retirement_date="2026-06-01", as_of_date=as_of_date) == "Prioritario"
    assert priority_label(retirement_date="2026-12-01", as_of_date=as_of_date) == "Da pianificare"
    assert priority_label(retirement_date="2028-01-01", as_of_date=as_of_date) == "Debito"
    assert priority_label(retirement_date="", as_of_date=as_of_date) == "Debito"
