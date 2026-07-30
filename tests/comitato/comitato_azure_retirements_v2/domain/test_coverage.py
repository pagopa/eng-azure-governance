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
