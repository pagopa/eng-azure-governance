import errno
import os
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
    support_staging = destination.with_name(f"{destination.name}-support") / ".staging"
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


def test_publish_can_stage_exports_and_support_on_separate_filesystems(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exports = tmp_path / "exports"
    support = tmp_path / "support"
    replace_path = os.replace

    def replace_on_same_filesystem(source: Path, destination: Path) -> None:
        if source.is_relative_to(exports) != destination.is_relative_to(exports):
            raise OSError(errno.EXDEV, "cross-device rename")
        replace_path(source, destination)

    monkeypatch.setattr(os, "replace", replace_on_same_filesystem)

    receipt = FilesystemAtomicPublicationStore(exports, support).publish(
        empty_candidate()
    )

    assert (
        exports / receipt.current_reference / "03_azure_retirements_slide.xlsx"
    ).is_file()
    monthly_support = support / receipt.current_reference
    assert (monthly_support / "01_azure_advisor_retirements_raw.jsonl").is_file()
    assert (monthly_support / "publication-manifest.json").is_file()


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
        tmp_path.with_name(f"{tmp_path.name}-support") / "2026" / "07" / "sentinel.json"
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
        FaultInjectingPublicationStore(tmp_path, fault=fault).publish(empty_candidate())

    assert read_monthly_tree(tmp_path, date(2026, 7, 30)) == export_before
    assert read_monthly_support_tree(tmp_path, date(2026, 7, 30)) == support_before


@pytest.mark.parametrize("interrupt_during", ["backup", "switch"])
def test_interrupt_during_rename_restores_the_previous_month(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, interrupt_during: str
) -> None:
    _seed(tmp_path)
    month = date(2026, 7, 30)
    exports = tmp_path / "2026" / "07"
    export_before = read_monthly_tree(tmp_path, month)
    support_before = read_monthly_support_tree(tmp_path, month)
    replace_path = os.replace

    def interrupt_after_rename(source: Path, destination: Path) -> None:
        replace_path(source, destination)
        if interrupt_during == "backup" and source == exports:
            raise KeyboardInterrupt
        if interrupt_during == "switch" and destination == exports:
            if not source.name.endswith("-previous"):
                raise KeyboardInterrupt

    monkeypatch.setattr(os, "replace", interrupt_after_rename)
    with pytest.raises(KeyboardInterrupt):
        FilesystemAtomicPublicationStore(tmp_path).publish(empty_candidate())

    assert read_monthly_tree(tmp_path, month) == export_before
    assert read_monthly_support_tree(tmp_path, month) == support_before
    assert _private_entries(tmp_path) == ((), (), ())


def test_payload_changed_after_read_does_not_replace_the_previous_month(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exports = tmp_path / "exports"
    support = tmp_path / "support"
    store = FilesystemAtomicPublicationStore(exports, support)
    month = store.publish(empty_candidate()).current_reference
    artifact = "01_azure_advisor_retirements_raw.jsonl"
    prior_payload = (support / month / artifact).read_bytes()
    prior_manifest = (support / month / "publication-manifest.json").read_bytes()
    prior_workbook = (exports / month / "03_azure_retirements_slide.xlsx").read_bytes()

    def change_after_read(_candidate, point: str, logical_path: str = "") -> None:
        if point == "hash" and logical_path == artifact:
            (staged,) = (support / ".staging").iterdir()
            (staged / artifact).write_bytes(b'{"changed":true}\n')

    monkeypatch.setattr(store, "_inject_fault", change_after_read)
    with pytest.raises(PublicationError) as raised:
        store.publish(empty_candidate())

    (diagnostic,) = raised.value.diagnostics
    assert (diagnostic.code, diagnostic.artifact) == ("staged_bytes_changed", artifact)
    assert (support / month / artifact).read_bytes() == prior_payload
    assert (
        support / month / "publication-manifest.json"
    ).read_bytes() == prior_manifest
    assert (
        exports / month / "03_azure_retirements_slide.xlsx"
    ).read_bytes() == prior_workbook


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
