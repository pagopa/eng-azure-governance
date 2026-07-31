from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements_v2.adapters.filesystem_publication import (
    FaultInjectingPublicationStore,
    FilesystemAtomicPublicationStore,
)
from tests.comitato.comitato_azure_retirements_v2.publication.filesystem_support import (
    read_current_tree,
)
from src.comitato.comitato_azure_retirements_v2.publication.model import PublicationError
from tests.comitato.comitato_azure_retirements_v2.publication.test_empty_publication import (
    empty_candidate,
)


def _seed(destination: Path) -> tuple[bytes, bytes]:
    generation = destination / "generations" / "seed"
    generation.mkdir(parents=True)
    (generation / "sentinel.txt").write_bytes(b"seeded-current")
    (destination / "current").write_bytes(b"generations/seed\n")
    return (destination / "current").read_bytes(), (generation / "sentinel.txt").read_bytes()


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


def test_store_rejects_destination_capability_mismatch(tmp_path: Path) -> None:
    destination = tmp_path / "destination-file"
    destination.write_bytes(b"not-a-directory")

    with pytest.raises(PublicationError):
        FilesystemAtomicPublicationStore(destination).publish(empty_candidate())


def test_publish_exposes_one_complete_generation(tmp_path: Path) -> None:
    store = FilesystemAtomicPublicationStore(tmp_path)

    receipt = store.publish(empty_candidate())

    assert (tmp_path / "current").read_text(encoding="utf-8") == (
        f"generations/{receipt.generation}\n"
    )
    assert read_current_tree(tmp_path)["publication-manifest.json"]


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
    generations_before = tuple(
        sorted(path.name for path in (tmp_path / "generations").iterdir())
    )
    store = FaultInjectingPublicationStore(tmp_path, fault=fault)

    with pytest.raises(PublicationError):
        store.publish(empty_candidate())

    assert (
        (tmp_path / "current").read_bytes(),
        (tmp_path / "generations" / "seed" / "sentinel.txt").read_bytes(),
    ) == published_before
    assert _private_entries(tmp_path) == private_before
    assert tuple(
        sorted(path.name for path in (tmp_path / "generations").iterdir())
    ) == generations_before


def test_success_switches_one_current_reference_and_publishes_complete_generation(tmp_path: Path) -> None:
    _seed(tmp_path)
    store = FilesystemAtomicPublicationStore(tmp_path)

    receipt = store.publish(empty_candidate())

    assert (tmp_path / "current").read_text() == f"generations/{receipt.generation}\n"
    assert read_current_tree(tmp_path)["publication-manifest.json"]


def test_post_commit_cleanup_failure_is_warning_and_does_not_roll_back(tmp_path: Path) -> None:
    _seed(tmp_path)
    store = FaultInjectingPublicationStore(tmp_path, fault="cleanup")

    receipt = store.publish(empty_candidate())

    assert (tmp_path / "generations" / receipt.generation).is_dir()
    assert store.warnings == ("superseded generation cleanup failed",)
    assert read_current_tree(tmp_path)["publication-manifest.json"]
