from __future__ import annotations

from src.comitato.comitato_azure_retirements_v2.domain.coverage import validate_platform_coverage
from src.comitato.comitato_azure_retirements_v2.domain.platforms import PlatformCatalogSnapshot


def test_coverage_reports_scope_and_evidence_missing_uuids_once() -> None:
    first = "11111111-1111-1111-1111-111111111111"
    second = "22222222-2222-2222-2222-222222222222"
    result = validate_platform_coverage(
        (second, first, first),
        ({"subscription_id": first, "raw_record_ref": "ref-b"}, {"subscription_id": second, "raw_record_ref": "ref-a"}),
        PlatformCatalogSnapshot(schema_version=1, sha256="a" * 64, assignments=()),
        report="all",
        run_id="run-1",
    )
    assert [item.subscription_id for item in result.diagnostics] == [first, second]
    assert result.diagnostics[0].context


def test_coverage_uses_azure_name_and_sorted_record_refs() -> None:
    subscription_id = "11111111-1111-1111-1111-111111111111"
    result = validate_platform_coverage(
        (),
        (
            {
                "subscription_id": subscription_id.upper(),
                "subscription_name": "Azure display name",
                "raw_record_ref": "ref-z",
            },
            {
                "subscription_id": subscription_id,
                "subscription_name": "Azure display name",
                "raw_record_ref": "ref-a",
            },
        ),
        PlatformCatalogSnapshot(schema_version=1, sha256="a" * 64, assignments=()),
        report="advisor",
        run_id="run-1",
    )
    diagnostic = result.diagnostics[0]
    assert diagnostic.message == (
        "Publication blocked: subscription Azure display name "
        f"({subscription_id}) has no active assignment in "
        "src/_source_of_truth/eng-finops-platforms.yaml"
    )
    assert dict(diagnostic.context) == {
        "subscription_name": "Azure display name",
        "record_refs": "ref-a,ref-z",
    }


def test_coverage_keeps_scope_only_context_without_record_refs() -> None:
    subscription_id = "11111111-1111-1111-1111-111111111111"
    result = validate_platform_coverage(
        (subscription_id,),
        (),
        PlatformCatalogSnapshot(schema_version=1, sha256="a" * 64, assignments=()),
    )
    assert dict(result.diagnostics[0].context)["record_refs"] == ""


def test_global_rows_with_no_subscription_do_not_get_all_fallback() -> None:
    result = validate_platform_coverage(
        (),
        ({"record_type": "service_health_event_global"},),
        PlatformCatalogSnapshot(schema_version=1, sha256="a" * 64, assignments=()),
    )
    assert result.is_valid
