from datetime import date
from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements_v2.adapters.filesystem_publication import (
    FaultInjectingPublicationStore,
    FilesystemAtomicPublicationStore,
)
from tests.comitato.comitato_azure_retirements_v2.publication.filesystem_support import (
    read_monthly_tree,
)
from src.comitato.comitato_azure_retirements_v2.publication.model import PublicationError
from src.comitato.comitato_azure_retirements_v2.ports import RuntimeEvent
from tests.comitato.comitato_azure_retirements_v2.publication.test_empty_publication import (
    empty_candidate,
)


def _seed(destination: Path) -> bytes:
    monthly_bundle = destination / "2026" / "07"
    monthly_bundle.mkdir(parents=True)
    (monthly_bundle / "sentinel.txt").write_bytes(b"seeded-current")
    return (monthly_bundle / "sentinel.txt").read_bytes()


def _private_entries(destination: Path) -> tuple[tuple[str, ...], tuple[str, ...]]:
    staging = destination / ".staging"
    temporary_references = tuple(
        sorted(path.name for path in destination.glob(".current-*.tmp"))
    )
    staged_generations = (
        tuple(sorted(path.name for path in staging.iterdir()))
        if staging.exists()
        else ()
    )
    return staged_generations, temporary_references


class RecordingRunObserver:
    def __init__(self) -> None:
        self.events: list[RuntimeEvent] = []

    def emit(self, event: RuntimeEvent) -> None:
        self.events.append(event)


def test_store_rejects_destination_capability_mismatch(tmp_path: Path) -> None:
    destination = tmp_path / "destination-file"
    destination.write_bytes(b"not-a-directory")

    with pytest.raises(PublicationError):
        FilesystemAtomicPublicationStore(destination).publish(empty_candidate())


def test_publish_exposes_one_complete_monthly_bundle(tmp_path: Path) -> None:
    store = FilesystemAtomicPublicationStore(tmp_path)

    receipt = store.publish(empty_candidate())

    assert receipt.generation == "2026/07"
    assert receipt.current_reference == "2026/07"
    assert read_monthly_tree(tmp_path, date(2026, 7, 30))["publication-manifest.json"]
    assert not (tmp_path / "current").exists()
    assert not (tmp_path / "generations").exists()


def test_publish_emits_atomic_publication_events(tmp_path: Path) -> None:
    observer = RecordingRunObserver()
    store = FilesystemAtomicPublicationStore(tmp_path, observer=observer)

    store.publish(empty_candidate())

    event_names = [event.event for event in observer.events]
    assert "publication_preflight" in event_names
    assert "publication_staging_started" in event_names
    assert "publication_staging_completed" in event_names
    assert "publication_switch_started" in event_names
    assert "publication_completed" in event_names
    assert {event.run_id for event in observer.events} == {empty_candidate().context.run_id}


def test_cleanup_warning_emits_publication_event(tmp_path: Path) -> None:
    _seed(tmp_path)
    observer = RecordingRunObserver()
    store = FaultInjectingPublicationStore(tmp_path, fault="cleanup", observer=observer)

    store.publish(empty_candidate())

    assert any(event.event == "publication_cleanup_warning" for event in observer.events)


def test_publish_replaces_the_complete_monthly_bundle(tmp_path: Path) -> None:
    store = FilesystemAtomicPublicationStore(tmp_path)
    july = tmp_path / "2026" / "07"
    august = tmp_path / "2026" / "08"
    july.mkdir(parents=True)

    store.publish(empty_candidate())
    (july / "stale-artifact.tsv").write_bytes(b"stale")

    second_july_receipt = store.publish(empty_candidate())

    assert second_july_receipt.current_reference == "2026/07"
    assert not (july / "stale-artifact.tsv").exists()
    assert (july / "publication-manifest.json").is_file()
    assert not (tmp_path / "current").exists()
    assert not (tmp_path / "generations").exists()

    store.publish(empty_candidate(as_of_date=date(2026, 8, 1)))

    assert (july / "publication-manifest.json").is_file()
    assert (august / "publication-manifest.json").is_file()


def test_store_exposes_only_publish_as_the_transaction_operation(
    tmp_path: Path,
) -> None:
    store = FilesystemAtomicPublicationStore(tmp_path)

    assert callable(store.publish)
    assert not hasattr(store, "stage")
    assert not hasattr(store, "commit")
    assert not hasattr(store, "preflight")


@pytest.mark.parametrize(
    "fault",
    ("flush", "sync", "close", "hash", "reread", "before_switch", "durable_marker"),
)
def test_precommit_fault_restores_complete_publication_state(
    tmp_path: Path,
    fault: str,
) -> None:
    published_before = _seed(tmp_path)
    private_before = _private_entries(tmp_path)
    store = FaultInjectingPublicationStore(tmp_path, fault=fault)

    with pytest.raises(PublicationError):
        store.publish(empty_candidate())

    assert (tmp_path / "2026" / "07" / "sentinel.txt").read_bytes() == published_before
    assert _private_entries(tmp_path) == private_before
    assert not (tmp_path / "current").exists()
    assert not (tmp_path / "generations").exists()


def test_success_replaces_one_monthly_bundle_with_complete_artifacts(tmp_path: Path) -> None:
    _seed(tmp_path)
    store = FilesystemAtomicPublicationStore(tmp_path)

    receipt = store.publish(empty_candidate())

    assert receipt.current_reference == "2026/07"
    assert read_monthly_tree(tmp_path, date(2026, 7, 30))["publication-manifest.json"]


def test_post_commit_cleanup_failure_is_warning_and_does_not_roll_back(tmp_path: Path) -> None:
    _seed(tmp_path)
    store = FaultInjectingPublicationStore(tmp_path, fault="cleanup")

    receipt = store.publish(empty_candidate())

    assert (tmp_path / receipt.current_reference).is_dir()
    assert store.warnings == ("superseded monthly bundle cleanup failed",)
    assert read_monthly_tree(tmp_path, date(2026, 7, 30))["publication-manifest.json"]
