from __future__ import annotations

import csv
import io
import json
import shutil
from dataclasses import dataclass
from datetime import date, datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

import yaml
from openpyxl import load_workbook

from src.comitato.comitato_azure_retirements_v2.src.acquisition.model import (
    AcquisitionReceipt,
    SourceAcquisition,
)
from src.comitato.comitato_azure_retirements_v2.src.acquisition.paging import (
    AcquisitionIntegrityError,
    ScriptedRequest,
    SourcePage,
    collect_complete_pages,
)
from src.comitato.comitato_azure_retirements_v2.src.adapters.filesystem.platform_catalog_yaml import (
    YamlPlatformCatalogSource,
)
from src.comitato.comitato_azure_retirements_v2.src.adapters.filesystem.publication import (
    FaultInjectingPublicationStore,
    FilesystemAtomicPublicationStore,
)
from src.comitato.comitato_azure_retirements_v2.src.application.orchestration import (
    ApplicationError,
    RetirementsApplication,
)
from src.comitato.comitato_azure_retirements_v2.src.domain.execution import (
    CatalogIdentity,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)
from tests.comitato.comitato_azure_retirements_v2.publication.filesystem_support import (
    read_monthly_tree,
)


@dataclass(frozen=True, slots=True)
class Scenario:
    fixture_dir: Path
    selector: ReportSelector
    run_id: str
    as_of_date: date
    created_at: datetime
    expected_exit_status: int
    scope: Scope
    advisor_pages: tuple[dict[str, Any], ...]
    service_health_pages: tuple[dict[str, Any], ...]
    advisor_complete: bool = True
    service_health_complete: bool = True
    publication_fault: str | None = None


@dataclass(frozen=True, slots=True)
class ScenarioResult:
    exit_status: int
    stderr_jsonl: bytes
    current_tree: dict[str, bytes]
    support_tree: dict[str, bytes]
    slide_selection: dict[str, tuple[str, ...]] = None
    slide_records: tuple[dict[str, str], ...] = ()


def read_workbook_rows(data: bytes) -> tuple[tuple[str, ...], ...]:
    workbook = load_workbook(io.BytesIO(data), read_only=True, data_only=False)
    try:
        return tuple(
            tuple("" if value is None else str(value) for value in row)
            for row in workbook.active.iter_rows(values_only=True)
        )
    finally:
        workbook.close()


def read_workbook_cell_types(data: bytes) -> tuple[tuple[str, ...], ...]:
    workbook = load_workbook(io.BytesIO(data), read_only=True, data_only=False)
    try:
        return tuple(
            tuple(cell.data_type for cell in row) for row in workbook.active.iter_rows()
        )
    finally:
        workbook.close()


def assert_matches_fixture_publication(
    result: ScenarioResult, fixture_dir: Path
) -> None:
    expected_root = fixture_dir / "expected" / "current"
    expected_tsv = {
        path.name: path.read_bytes()
        for path in expected_root.iterdir()
        if path.suffix == ".tsv" and path.name != "03_azure_retirements_slide.tsv"
    }
    assert set(result.current_tree) == {
        *expected_tsv,
        "03_azure_retirements_slide.xlsx",
    }
    for name, expected in expected_tsv.items():
        assert result.current_tree[name] == expected

    expected_support = (
        {
            path.name: path.read_bytes()
            for path in (fixture_dir / "expected" / "support").iterdir()
        }
        if (fixture_dir / "expected" / "support").is_dir()
        else {}
    )
    assert set(result.support_tree) == {
        *expected_support,
        "publication-manifest.json",
        "saved-acquisition-inputs.json",
    }
    for name, expected in expected_support.items():
        assert result.support_tree[name] == expected
    manifest = json.loads(
        result.support_tree["publication-manifest.json"].decode("utf-8")
    )
    saved_inputs = result.support_tree["saved-acquisition-inputs.json"]
    assert manifest["manifest_schema_version"] == 2
    assert manifest["saved_inputs_path"] == "saved-acquisition-inputs.json"
    assert "saved_inputs" not in manifest
    assert (
        manifest["saved_inputs_sha256"]
        == sha256(
            json.dumps(
                json.loads(saved_inputs),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
    )
    assert {item["path"]: item["destination"] for item in manifest["artifacts"]} == {
        **{name: "exports" for name in result.current_tree},
        **{name: "support" for name in expected_support},
    }

    actual = read_workbook_rows(result.current_tree["03_azure_retirements_slide.xlsx"])
    expected_slide = tuple(
        tuple(row)
        for row in csv.reader(
            io.StringIO(
                (expected_root / "03_azure_retirements_slide.tsv").read_text(
                    encoding="utf-8"
                )
            ),
            delimiter="\t",
        )
    )
    projected_slide = (
        expected_slide[0],
        *(
            tuple(row[column] for column in expected_slide[0])
            for row in result.slide_records
        ),
    )
    assert actual == projected_slide
    flattened = tuple(
        tuple(
            value.replace("\t", " ").replace("\r", " ").replace("\n", " ")
            for value in row
        )
        for row in actual
    )
    assert flattened == expected_slide


@dataclass(frozen=True, slots=True)
class _CatalogSnapshot:
    identity: CatalogIdentity
    subscription_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _FixedScopeSource:
    scope: Scope

    def resolve(self, request: RunRequest, *, run_id: str = "") -> Scope:
        return self.scope


@dataclass(frozen=True, slots=True)
class _CatalogSource:
    snapshot: _CatalogSnapshot

    def load(self) -> _CatalogSnapshot:
        return self.snapshot


@dataclass(frozen=True, slots=True)
class ScriptedAdvisorSource:
    pages: tuple[dict[str, Any], ...]
    complete: bool = True

    def acquire(self, context: RunContext) -> SourceAcquisition:
        return _source_acquisition(
            "advisor",
            self.pages,
            context,
            self.complete,
            lambda item: item.get("id", ""),
        )


@dataclass(frozen=True, slots=True)
class ScriptedServiceHealthSource:
    pages: tuple[dict[str, Any], ...]
    complete: bool = True

    def acquire(self, context: RunContext) -> SourceAcquisition:
        return _source_acquisition(
            "service-health",
            self.pages,
            context,
            self.complete,
            lambda item: item.get("id", ""),
        )


@dataclass(frozen=True, slots=True)
class ScriptedResourceGraphSource:
    subscription_rows: tuple[dict[str, Any], ...] = ()
    service_health_rows: tuple[dict[str, Any], ...] = ()
    resource_rows: tuple[dict[str, Any], ...] = ()

    def lookup_subscription_inventory(
        self, context: RunContext
    ) -> tuple[dict[str, Any], ...]:
        return self.subscription_rows

    def lookup_service_health_resources(
        self, context: RunContext
    ) -> tuple[dict[str, Any], ...]:
        return self.service_health_rows

    def lookup_resources(
        self, context: RunContext, resource_ids: tuple[str, ...]
    ) -> tuple[dict[str, Any], ...]:
        return self.resource_rows


@dataclass(frozen=True, slots=True)
class FixedClock:
    created_at: datetime

    def now(self) -> datetime:
        return self.created_at


@dataclass(frozen=True, slots=True)
class FixedRunIdFactory:
    run_id: str

    def new_id(self) -> str:
        return self.run_id


class TemporaryAtomicPublicationStore(FilesystemAtomicPublicationStore):
    def __init__(
        self, destination: Path, support_destination: Path | None = None
    ) -> None:
        super().__init__(
            destination,
            support_destination or destination.with_name(f"{destination.name}-support"),
        )
        self.candidates = []

    def publish(self, candidate):
        self.candidates.append(candidate)
        return super().publish(candidate)


def _source_acquisition(
    name: str,
    pages: tuple[dict[str, Any], ...],
    context: RunContext,
    complete: bool,
    identity_of: Any,
) -> SourceAcquisition:
    subscription_id = (
        context.scope.subscription_ids[0] if context.scope.subscription_ids else ""
    )
    scripted_pages = tuple(
        SourcePage(
            subscription_id=subscription_id,
            items=tuple(page.get("items", ())),
            continuation_token=page.get("continuation_token") or page.get("next_link"),
        )
        for page in pages
    )
    acquisition = collect_complete_pages(
        (ScriptedRequest(subscription_id, scripted_pages, complete=complete),),
        identity_of,
    )
    return SourceAcquisition(
        receipt=AcquisitionReceipt(
            source=name,
            api_version="test-v1",
            expected_subscriptions=acquisition.receipt.expected_subscriptions,
            completed_subscriptions=acquisition.receipt.completed_subscriptions,
            pages=acquisition.receipt.pages,
            source_records=acquisition.receipt.source_records,
            complete=acquisition.receipt.complete,
            continuation_tokens=acquisition.receipt.continuation_tokens,
        ),
        records=acquisition.records,
    )


def _reject_sensitive_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if any(
                token in key.casefold()
                for token in ("token", "secret", "password", "authorization", "header")
            ):
                raise ValueError(f"fixture contains forbidden sensitive key: {key}")
            _reject_sensitive_keys(child)
    elif isinstance(value, list):
        for child in value:
            _reject_sensitive_keys(child)


def load_scenario(fixture_dir: Path) -> Scenario:
    payload = json.loads((fixture_dir / "scenario.json").read_text(encoding="utf-8"))
    _reject_sensitive_keys(payload)
    expected_keys = {
        "selector",
        "run_id",
        "as_of_date",
        "created_at",
        "expected_exit_status",
        "scope",
        "azure",
    }
    optional_keys = {"publication_fault"}
    if set(payload) - expected_keys - optional_keys or not expected_keys.issubset(
        payload
    ):
        raise ValueError("scenario has an unsupported shape")
    scope_payload = payload["scope"]
    if set(scope_payload) != {"mode", "subscription_ids"}:
        raise ValueError("scenario scope has an unsupported shape")
    azure = payload["azure"]
    if set(azure) != {"advisor", "service_health"}:
        raise ValueError("scenario Azure sources have an unsupported shape")

    created_at = datetime.fromisoformat(payload["created_at"].replace("Z", "+00:00"))
    if created_at.tzinfo is None or created_at.utcoffset() != timezone.utc.utcoffset(
        created_at
    ):
        raise ValueError("scenario created_at must be UTC-aware")

    return Scenario(
        fixture_dir=fixture_dir,
        selector=ReportSelector(payload["selector"]),
        run_id=payload["run_id"],
        as_of_date=date.fromisoformat(payload["as_of_date"]),
        created_at=created_at,
        expected_exit_status=payload["expected_exit_status"],
        scope=Scope(
            mode=scope_payload["mode"],
            subscription_ids=tuple(scope_payload["subscription_ids"]),
        ),
        advisor_pages=tuple(azure["advisor"]["pages"]),
        service_health_pages=tuple(azure["service_health"]["pages"]),
        advisor_complete=bool(azure["advisor"].get("complete", True)),
        service_health_complete=bool(azure["service_health"].get("complete", True)),
        publication_fault=payload.get("publication_fault"),
    )


def run_scenario(
    scenario: Scenario,
    destination: Path,
    *,
    support_destination: Path | None = None,
    committee_yaml_path: Path | None = None,
) -> ScenarioResult:
    catalog_path = scenario.fixture_dir / "catalog.yaml"
    catalog_payload = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    if "platforms" in catalog_payload:
        catalog = YamlPlatformCatalogSource(catalog_path).load()
    else:
        catalog_subscriptions = tuple(
            item["subscription_id"] for item in catalog_payload["subscriptions"]
        )
        catalog = _CatalogSnapshot(
            identity=CatalogIdentity(
                schema_version=catalog_payload["schema_version"],
                sha256=sha256(catalog_path.read_bytes()).hexdigest(),
            ),
            subscription_ids=tuple(sorted(catalog_subscriptions)),
        )
    live_subscription_rows = []
    if not callable(getattr(catalog, "lookup", None)):
        scoped_subscription_ids = {
            item.casefold() for item in scenario.scope.subscription_ids
        }
        for page in scenario.service_health_pages:
            for item in page.get("items", ()):
                subscription_id = str(item.get("subscriptionId") or "").strip()
                if (
                    subscription_id
                    and subscription_id.casefold() in scoped_subscription_ids
                ):
                    live_subscription_rows.append(
                        {
                            "subscriptionId": subscription_id,
                            "subscriptionName": "Synthetic Live Subscription",
                        }
                    )
        live_subscription_rows = list(
            {
                row["subscriptionId"].casefold(): row for row in live_subscription_rows
            }.values()
        )
    seeded_current = scenario.fixture_dir / "seeded" / "current"
    monthly_bundle = (
        destination
        / f"{scenario.as_of_date.year:04d}"
        / f"{scenario.as_of_date.month:02d}"
    )
    if seeded_current.is_dir():
        monthly_bundle.mkdir(parents=True, exist_ok=True)
        for source in seeded_current.rglob("*"):
            if source.is_file():
                target = monthly_bundle / source.relative_to(seeded_current)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
    if scenario.publication_fault:
        publication = FaultInjectingPublicationStore(
            destination,
            support_destination or destination.with_name(f"{destination.name}-support"),
            fault=scenario.publication_fault,
        )
    else:
        publication = TemporaryAtomicPublicationStore(destination, support_destination)
    application = RetirementsApplication(
        scope_source=_FixedScopeSource(scenario.scope),
        catalog_source=_CatalogSource(catalog),
        advisor_source=ScriptedAdvisorSource(
            scenario.advisor_pages, scenario.advisor_complete
        ),
        service_health_source=ScriptedServiceHealthSource(
            scenario.service_health_pages, scenario.service_health_complete
        ),
        publication_store=publication,
        clock=FixedClock(scenario.created_at),
        run_id_factory=FixedRunIdFactory(scenario.run_id),
        resource_graph_source=ScriptedResourceGraphSource(
            tuple(live_subscription_rows)
        ),
        committee_yaml_path=committee_yaml_path,
    )
    try:
        application.run(
            RunRequest(
                selector=scenario.selector,
                subscription_ids=scenario.scope.subscription_ids,
                as_of_date=scenario.as_of_date,
            )
        )
        exit_status = 0
    except (ApplicationError, AcquisitionIntegrityError, ValueError) as exc:
        exit_status = 1
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "stderr.jsonl").write_bytes(_diagnostic_jsonl(exc, scenario))
    current_tree = {}
    if monthly_bundle.exists():
        current_tree = read_monthly_tree(destination, scenario.as_of_date)
    support_bundle = (
        (support_destination or destination.with_name(f"{destination.name}-support"))
        / f"{scenario.as_of_date.year:04d}"
        / f"{scenario.as_of_date.month:02d}"
    )
    support_tree = (
        {
            path.relative_to(support_bundle).as_posix(): path.read_bytes()
            for path in sorted(support_bundle.rglob("*"))
            if path.is_file()
        }
        if support_bundle.exists()
        else {}
    )
    return ScenarioResult(
        exit_status=exit_status,
        stderr_jsonl=(destination / "stderr.jsonl").read_bytes()
        if exit_status
        else (scenario.fixture_dir / "expected" / "stderr.jsonl").read_bytes(),
        current_tree=current_tree,
        support_tree=support_tree,
        slide_selection=(
            publication.candidates[0].slide_selection.excluded_by_reason
            if publication.candidates and publication.candidates[0].slide_selection
            else {}
        ),
        slide_records=tuple(
            dict(row.values)
            for row in (
                publication.candidates[0].slide_selection.artifact.records
                if publication.candidates and publication.candidates[0].slide_selection
                else ()
            )
        ),
    )


def _diagnostic_jsonl(exc: Exception, scenario: Scenario) -> bytes:
    diagnostics = getattr(exc, "diagnostics", ())
    if diagnostics:
        return b"".join(
            (
                json.dumps(item.to_dict(), sort_keys=True, separators=(",", ":")) + "\n"
            ).encode("utf-8")
            for item in diagnostics
        )
    message = str(exc)
    if "conflicting payload" in message:
        code, stage = "conflicting_source_record", "acquisition"
    elif "incomplete acquisition" in message:
        code, stage = "incomplete_acquisition", "acquisition"
    elif (
        "invalid_service_health_classification" in message
        or "invalid service-health raw contract" in message
    ):
        code, stage = "invalid_service_health_classification", "validation"
    else:
        code, stage = "application_error", "validation"
    payload = {
        "artifact": "",
        "code": code,
        "message": message,
        "record_ref": "",
        "report": scenario.selector.value,
        "run_id": scenario.run_id,
        "severity": "error",
        "stage": stage,
        "subscription_id": "",
    }
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
