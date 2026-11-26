from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements_v2.src.adapters.filesystem.publication import (
    FaultInjectingPublicationStore,
    FilesystemAtomicPublicationStore,
)
from src.comitato.comitato_azure_retirements_v2.src.ports import RuntimeEvent
from src.comitato.comitato_azure_retirements_v2.src.publication.model import (
    PublicationError,
)
from tests.comitato.comitato_azure_retirements_v2.publication.filesystem_support import (
    read_monthly_support_tree,
    read_monthly_tree,
)
from tests.comitato.comitato_azure_retirements_v2.publication.test_empty_publication import (
    empty_candidate,
)


def _seed(destination: Path) -> bytes:
    monthly_bundle = destination / "2026" / "07"
    monthly_bundle.mkdir(parents=True)
    (monthly_bundle / "sentinel.txt").write_bytes(b"seeded-current")
    support_bundle = (
        destination.with_name(f"{destination.name}-support") / "2026" / "07"
    )
    support_bundle.mkdir(parents=True)
    (support_bundle / "sentinel.json").write_bytes(b'{"prior":"support"}')
    return (monthly_bundle / "sentinel.txt").read_bytes()


def _private_entries(
    destination: Path,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    staging = destination / ".staging"
    support_staging = (
        destination.with_name(f"{destination.name}-support") / ".staging"
    )
    temporary_references = tuple(
        sorted(path.name for path in destination.glob(".current-*.tmp"))
    )
    staged_generations = (
        tuple(sorted(path.name for path in staging.iterdir()))
        if staging.exists()
        else ()
    )
    staged_support = (
        tuple(sorted(path.name for path in support_staging.iterdir()))
        if support_staging.exists()
        else ()
    )
    return staged_generations, staged_support, temporary_references


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


def test_publish_accepts_relative_destination_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    destination = Path("relative-destination")

    receipt = FilesystemAtomicPublicationStore(destination).publish(empty_candidate())

    assert receipt.current_reference == "2026/07"
    assert (
        Path("relative-destination-support")
        / "2026"
        / "07"
        / "publication-manifest.json"
    ).is_file()


def test_publish_exposes_one_complete_monthly_bundle(tmp_path: Path) -> None:
    store = FilesystemAtomicPublicationStore(tmp_path)

    receipt = store.publish(empty_candidate())

    assert receipt.generation == "2026/07"
    assert receipt.current_reference == "2026/07"
    assert read_monthly_support_tree(tmp_path, date(2026, 7, 30))[
        "publication-manifest.json"
    ]
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
    assert {event.run_id for event in observer.events} == {
        empty_candidate().context.run_id
    }


def test_cleanup_warning_emits_publication_event(tmp_path: Path) -> None:
    _seed(tmp_path)
    observer = RecordingRunObserver()
    store = FaultInjectingPublicationStore(tmp_path, fault="cleanup", observer=observer)

    store.publish(empty_candidate())

    assert any(
        event.event == "publication_cleanup_warning" for event in observer.events
    )


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
    assert "publication-manifest.json" in read_monthly_support_tree(
        tmp_path, date(2026, 7, 30)
    )
    assert not (tmp_path / ".history").exists()
    assert not (tmp_path / "current").exists()
    assert not (tmp_path / "generations").exists()

    store.publish(empty_candidate(as_of_date=date(2026, 8, 1)))

    assert "publication-manifest.json" in read_monthly_support_tree(
        tmp_path, date(2026, 7, 30)
    )
    assert "publication-manifest.json" in read_monthly_support_tree(
        tmp_path, date(2026, 8, 1)
    )


def test_next_month_does_not_restore_an_editorial_sidecar(tmp_path: Path) -> None:
    store = FilesystemAtomicPublicationStore(tmp_path)
    editorial_yaml = "schema_version: 1\nitems:\n  - id: carried-forward\n"

    store.publish(empty_candidate(editorial_yaml=editorial_yaml))
    store.publish(empty_candidate(as_of_date=date(2026, 8, 1)))

    assert "comitato_editoriale.yaml" not in read_monthly_tree(
        tmp_path, date(2026, 7, 30)
    )
    assert "comitato_editoriale.yaml" not in read_monthly_tree(
        tmp_path, date(2026, 8, 1)
    )


def test_same_month_replacement_does_not_restore_an_editorial_sidecar(
    tmp_path: Path,
) -> None:
    store = FilesystemAtomicPublicationStore(tmp_path)
    edited_yaml = "schema_version: 1\nitems:\n  - id: edited-item\n"

    store.publish(empty_candidate(editorial_yaml=edited_yaml))
    store.publish(empty_candidate(editorial_yaml="schema_version: 1\nitems: []\n"))

    current = read_monthly_tree(tmp_path, date(2026, 7, 30))
    assert "comitato_editoriale.yaml" not in current
    assert not (tmp_path / ".history").exists()


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
    assert (
        tmp_path.with_name(f"{tmp_path.name}-support")
        / "2026"
        / "07"
        / "sentinel.json"
    ).read_bytes() == b'{"prior":"support"}'
    assert _private_entries(tmp_path) == private_before
    assert not (tmp_path / "current").exists()
    assert not (tmp_path / "generations").exists()


@pytest.mark.parametrize(
    "fault",
    (
        "after_export_backup",
        "after_export_switch",
        "after_support_backup",
        "after_support_switch",
    ),
)
def test_switch_fault_restores_export_and_support_generations(
    tmp_path: Path,
    fault: str,
) -> None:
    _seed(tmp_path)
    export_before = read_monthly_tree(tmp_path, date(2026, 7, 30))
    support_before = read_monthly_support_tree(tmp_path, date(2026, 7, 30))

    with pytest.raises(PublicationError):
        FaultInjectingPublicationStore(tmp_path, fault=fault).publish(
            empty_candidate()
        )

    assert read_monthly_tree(tmp_path, date(2026, 7, 30)) == export_before
    assert read_monthly_support_tree(tmp_path, date(2026, 7, 30)) == support_before


def test_post_switch_failure_restores_export_and_support_generations(
    tmp_path: Path,
) -> None:
    store = FilesystemAtomicPublicationStore(tmp_path)
    store.publish(empty_candidate())
    export_before = read_monthly_tree(tmp_path, date(2026, 7, 30))
    support_before = read_monthly_support_tree(tmp_path, date(2026, 7, 30))

    def fail_after_switch() -> None:
        raise OSError("committee sidecar write failed")

    with pytest.raises(PublicationError):
        store.publish(
            replace(
                empty_candidate(),
                after_switch=fail_after_switch,
            )
        )

    assert read_monthly_tree(tmp_path, date(2026, 7, 30)) == export_before
    assert read_monthly_support_tree(tmp_path, date(2026, 7, 30)) == support_before


def test_failed_replacement_keeps_prior_manifest_and_no_sidecar(tmp_path: Path) -> None:
    editorial_yaml = "schema_version: 1\nitems:\n  - id: prior-valid\n"
    FilesystemAtomicPublicationStore(tmp_path).publish(
        empty_candidate(editorial_yaml=editorial_yaml)
    )
    store = FaultInjectingPublicationStore(tmp_path, fault="before_switch")

    with pytest.raises(PublicationError):
        store.publish(empty_candidate(as_of_date=date(2026, 7, 31)))

    current = read_monthly_tree(tmp_path, date(2026, 7, 30))
    support = read_monthly_support_tree(tmp_path, date(2026, 7, 30))
    assert "comitato_editoriale.yaml" not in current
    assert support["publication-manifest.json"]


def test_success_replaces_one_monthly_bundle_with_complete_artifacts(
    tmp_path: Path,
) -> None:
    _seed(tmp_path)
    store = FilesystemAtomicPublicationStore(tmp_path)

    receipt = store.publish(empty_candidate())

    assert receipt.current_reference == "2026/07"
    assert read_monthly_support_tree(tmp_path, date(2026, 7, 30))[
        "publication-manifest.json"
    ]


def test_post_commit_cleanup_failure_is_warning_and_does_not_roll_back(
    tmp_path: Path,
) -> None:
    _seed(tmp_path)
    store = FaultInjectingPublicationStore(tmp_path, fault="cleanup")

    receipt = store.publish(empty_candidate())

    assert (tmp_path / receipt.current_reference).is_dir()
    assert store.warnings == ("superseded monthly bundle cleanup failed",)
    assert read_monthly_support_tree(tmp_path, date(2026, 7, 30))[
        "publication-manifest.json"
    ]
