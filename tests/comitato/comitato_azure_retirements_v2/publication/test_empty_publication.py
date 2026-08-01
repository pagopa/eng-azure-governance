import json
from dataclasses import replace
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements_v2.acquisition.model import (
    AcquisitionReceipt,
    SourceAcquisition,
)
from src.comitato.comitato_azure_retirements_v2.contracts import (
    AGGREGATE_V1,
    SLIDES_V1,
)
from src.comitato.comitato_azure_retirements_v2.reports.advisor import ADVISOR_REPORT
from src.comitato.comitato_azure_retirements_v2.reports.catalog import DEFAULT_REPORT_CATALOG
from src.comitato.comitato_azure_retirements_v2.reports.service_health import SERVICE_HEALTH_REPORT
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)
from src.comitato.comitato_azure_retirements_v2.adapters.filesystem_publication import (
    FilesystemAtomicPublicationStore,
)
from src.comitato.comitato_azure_retirements_v2.adapters.filesystem_staging import (
    stage_candidate,
)
from src.comitato.comitato_azure_retirements_v2.publication.model import (
    PublicationCandidate,
    PublicationError,
)
from tests.comitato.comitato_azure_retirements_v2.publication.filesystem_support import (
    read_monthly_tree,
)


def empty_candidate(*, as_of_date: date = date(2026, 7, 30)) -> PublicationCandidate:
    context = RunContext(
        run_id="s06-empty",
        as_of_date=as_of_date,
        created_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
        request=RunRequest(selector=ReportSelector.ALL),
        scope=Scope(
            mode="explicit",
            subscription_ids=("11111111-1111-1111-1111-111111111111",),
        ),
        catalog_identity=CatalogIdentity(schema_version=1, sha256="e" * 64),
        dependency_plan=DependencyPlan(
            stages=("scope", "catalog", "advisor", "service-health", "aggregate", "slides", "publication")
        ),
    )
    advisor = ADVISOR_REPORT.contract.empty_artifact(context)
    service_health = SERVICE_HEALTH_REPORT.contract.empty_artifact(context)
    artifacts = (
        ADVISOR_REPORT.contract.encode(advisor),
        ADVISOR_REPORT.contract.encode_companion(advisor),
        SERVICE_HEALTH_REPORT.contract.encode(service_health),
        SERVICE_HEALTH_REPORT.contract.encode_companion(service_health),
        AGGREGATE_V1.encode(AGGREGATE_V1.empty_artifact(context)),
        SLIDES_V1.encode(SLIDES_V1.empty_artifact(context)),
    )
    acquisitions = (
        SourceAcquisition(
            receipt=AcquisitionReceipt("advisor", "test-v1", 1, 1, 1, 0, True)
        ),
        SourceAcquisition(
            receipt=AcquisitionReceipt("service-health", "test-v1", 1, 1, 1, 0, True)
        ),
    )
    return PublicationCandidate(
        context=context,
        report_closure=DEFAULT_REPORT_CATALOG.plan(ReportSelector.ALL),
        artifacts=artifacts,
        acquisitions=acquisitions,
    )


def _closure_with_custom_owners(candidate: PublicationCandidate):
    return replace(
        candidate.report_closure,
        path_owners=tuple(
            (path, replace(owner, name=f"custom-{owner.name}"))
            for path, owner in candidate.report_closure.path_owners
        ),
    )


def test_publish_manifest_uses_reread_bytes_and_exact_artifact_closure(tmp_path: Path) -> None:
    candidate = empty_candidate()
    store = FilesystemAtomicPublicationStore(tmp_path)

    receipt = store.publish(candidate)
    tree = read_monthly_tree(tmp_path, candidate.context.as_of_date)
    manifest = json.loads(tree["publication-manifest.json"])

    assert receipt.current_reference == "2026/07"
    assert [item["path"] for item in manifest["artifacts"]] == [
        artifact.logical_path for artifact in candidate.artifacts
    ]
    for item, artifact in zip(manifest["artifacts"], candidate.artifacts, strict=True):
        written = tree[artifact.logical_path]
        assert written == artifact.data
        assert item["bytes"] == len(written)
        assert item["sha256"] == artifact.digest


def test_staging_uses_candidate_closure_for_manifest_ownership(tmp_path: Path) -> None:
    candidate = empty_candidate()
    candidate = replace(
        candidate,
        report_closure=_closure_with_custom_owners(candidate),
    )

    staged = stage_candidate(candidate, tmp_path)
    reports = {
        item["path"]: item["report"]
        for item in staged.manifest["artifacts"]
    }

    assert reports["01_azure_advisor_retirements_raw.tsv"] == "custom-advisor"
    assert reports["03_azure_retirements_slide.tsv"] == "custom-slides"
    assert tuple(reports) == candidate.report_closure.expected_paths


def test_failed_commit_leaves_existing_current_generation_unchanged(tmp_path: Path) -> None:
    seeded = tmp_path / "2026" / "07"
    seeded.mkdir(parents=True)
    (seeded / "sentinel.txt").write_bytes(b"seeded-current")
    before = (seeded / "sentinel.txt").read_bytes()

    store = FilesystemAtomicPublicationStore(tmp_path, fail_before_switch=True)

    with pytest.raises(PublicationError, match="before monthly publication switch"):
        store.publish(empty_candidate())

    assert (seeded / "sentinel.txt").read_bytes() == before
