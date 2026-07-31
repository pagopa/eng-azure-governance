import json
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements_v2.acquisition.model import (
    AcquisitionReceipt,
    SourceAcquisition,
)
from src.comitato.comitato_azure_retirements_v2.contracts import (
    ADVISOR_V1,
    AGGREGATE_V1,
    SERVICE_HEALTH_V1,
    SLIDES_V1,
)
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
from src.comitato.comitato_azure_retirements_v2.publication.model import (
    PublicationCandidate,
    PublicationError,
)
from tests.comitato.comitato_azure_retirements_v2.publication.filesystem_support import (
    read_current_tree,
)


def empty_candidate() -> PublicationCandidate:
    context = RunContext(
        run_id="s06-empty",
        as_of_date=date(2026, 7, 30),
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
    advisor = ADVISOR_V1.empty_artifact(context)
    service_health = SERVICE_HEALTH_V1.empty_artifact(context)
    artifacts = (
        ADVISOR_V1.encode(advisor),
        ADVISOR_V1.encode_companion(advisor),
        SERVICE_HEALTH_V1.encode(service_health),
        SERVICE_HEALTH_V1.encode_companion(service_health),
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
    return PublicationCandidate(context, context.dependency_plan, artifacts, acquisitions)


def test_publish_manifest_uses_reread_bytes_and_exact_artifact_closure(tmp_path: Path) -> None:
    candidate = empty_candidate()
    store = FilesystemAtomicPublicationStore(tmp_path)

    receipt = store.publish(candidate)
    tree = read_current_tree(tmp_path)
    manifest = json.loads(tree["publication-manifest.json"])

    assert receipt.current_reference.startswith("generations/")
    assert [item["path"] for item in manifest["artifacts"]] == [
        artifact.logical_path for artifact in candidate.artifacts
    ]
    for item, artifact in zip(manifest["artifacts"], candidate.artifacts, strict=True):
        written = tree[artifact.logical_path]
        assert written == artifact.data
        assert item["bytes"] == len(written)
        assert item["sha256"] == artifact.digest


def test_failed_commit_leaves_existing_current_generation_unchanged(tmp_path: Path) -> None:
    seeded = tmp_path / "generations" / "seed"
    seeded.mkdir(parents=True)
    (seeded / "sentinel.txt").write_bytes(b"seeded-current")
    (tmp_path / "current").write_text("generations/seed\n", encoding="utf-8")
    before = (tmp_path / "current").read_bytes(), (seeded / "sentinel.txt").read_bytes()

    store = FilesystemAtomicPublicationStore(tmp_path, fail_before_switch=True)

    with pytest.raises(PublicationError, match="before atomic current switch"):
        store.publish(empty_candidate())

    assert ((tmp_path / "current").read_bytes(), (seeded / "sentinel.txt").read_bytes()) == before
