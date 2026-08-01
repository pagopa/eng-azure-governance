from pathlib import Path

from src.comitato.comitato_azure_retirements_v2.application.composition import build_application
from src.comitato.comitato_azure_retirements_v2.config import RuntimeConfig, parse_run_request
from src.comitato.comitato_azure_retirements_v2.adapters.arm_http import ArmHttpClient
from src.comitato.comitato_azure_retirements_v2.adapters.filesystem_publication import FilesystemAtomicPublicationStore
from src.comitato.comitato_azure_retirements_v2.adapters.platform_catalog_yaml import YamlPlatformCatalogSource
from src.comitato.comitato_azure_retirements_v2.adapters.resource_graph_api import ResourceGraphApiSource
from src.comitato.comitato_azure_retirements_v2.ports import RuntimeEvent


class RecordingObserver:
    def __init__(self) -> None:
        self.events: list[RuntimeEvent] = []

    def emit(self, event: RuntimeEvent) -> None:
        self.events.append(event)


def test_composition_injects_one_transport_catalog_and_publication_destination(tmp_path: Path) -> None:
    config = RuntimeConfig.from_request(
        parse_run_request(["--report", "advisor"]),
        catalog_path=tmp_path / "catalog.yaml",
        output_path=tmp_path / "published",
    )

    application = build_application(config)

    assert isinstance(getattr(application, "advisor_source").http, ArmHttpClient)
    assert getattr(application, "advisor_source").http is getattr(application, "service_health_source").http
    assert isinstance(application.catalog_source, YamlPlatformCatalogSource)
    assert application.catalog_source.path == tmp_path / "catalog.yaml"
    assert isinstance(application.publication_store, FilesystemAtomicPublicationStore)
    assert application.publication_store.destination == tmp_path / "published"


def test_composition_shares_transport_with_advisor_enrichment_sources(tmp_path: Path) -> None:
    config = RuntimeConfig.from_request(
        parse_run_request(["--report", "advisor"]),
        catalog_path=tmp_path / "catalog.yaml",
        output_path=tmp_path / "published",
    )

    application = build_application(config)
    enrichment = application.advisor_enrichment_source

    assert enrichment.metadata_source.http is application.advisor_source.http
    assert enrichment.resource_graph_source.http is application.advisor_source.http
    assert enrichment.metadata_source.api_version == config.api_versions.advisor
    assert enrichment.resource_graph_source.api_version == config.api_versions.resource_graph
    assert isinstance(application.resource_graph_source, ResourceGraphApiSource)
    assert application.resource_graph_source.http is application.advisor_source.http


def test_composition_injects_one_observer_into_application_transport_and_publication(
    tmp_path: Path,
) -> None:
    config = RuntimeConfig.from_request(
        parse_run_request(["--report", "advisor"]),
        catalog_path=tmp_path / "catalog.yaml",
        output_path=tmp_path / "published",
    )
    observer = RecordingObserver()

    application = build_application(config, observer=observer)

    assert application.observer is observer
    assert application.advisor_source.http._observer is observer
    assert application.publication_store._observer is observer
