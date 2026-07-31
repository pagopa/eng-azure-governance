from datetime import date, datetime, timezone

import pytest

from src.comitato.comitato_azure_retirements_v2.acquisition.model import (
    AcquisitionReceipt,
    SourceAcquisition,
)
from src.comitato.comitato_azure_retirements_v2.application.orchestration import ApplicationError
from src.comitato.comitato_azure_retirements_v2.application.raw_evidence import (
    prepare_raw_acquisition,
)
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)


def _context() -> RunContext:
    return RunContext(
        run_id="run-1",
        as_of_date=date(2026, 7, 31),
        created_at=datetime(2026, 7, 31, tzinfo=timezone.utc),
        request=RunRequest(ReportSelector.ADVISOR, ("sub-a",), date(2026, 7, 31)),
        scope=Scope(("sub-a",), mode="explicit"),
        catalog_identity=CatalogIdentity(1, "0" * 64),
        dependency_plan=DependencyPlan(("scope", "catalog", "advisor", "publication")),
    )


def _acquisition(*, complete: bool) -> SourceAcquisition:
    return SourceAcquisition(
        receipt=AcquisitionReceipt(
            source="advisor",
            api_version="test-v1",
            expected_subscriptions=1,
            completed_subscriptions=1 if complete else 0,
            pages=1,
            source_records=0,
            complete=complete,
        )
    )


def test_prepare_raw_acquisition_preserves_complete_empty_source() -> None:
    acquisition = _acquisition(complete=True)

    prepared = prepare_raw_acquisition(
        "advisor",
        acquisition,
        _context(),
    )

    assert prepared == acquisition


def test_prepare_raw_acquisition_rejects_incomplete_receipt() -> None:
    with pytest.raises(ApplicationError, match="incomplete advisor acquisition"):
        prepare_raw_acquisition(
            "advisor",
            _acquisition(complete=False),
            _context(),
        )
