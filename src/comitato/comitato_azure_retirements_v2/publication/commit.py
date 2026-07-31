from __future__ import annotations

from pathlib import Path

from .model import PublicationError, PublicationReceipt


def read_current_tree(destination: Path) -> dict[str, bytes]:
    reference = (destination / "current").read_text(encoding="utf-8").strip()
    current = destination / reference
    return {
        path.relative_to(current).as_posix(): path.read_bytes()
        for path in sorted(current.rglob("*"))
        if path.is_file()
    }


class AtomicFilesystemPublicationStore:
    """Lazy compatibility facade for the adapter-owned implementation."""

    def __new__(cls, *args, **kwargs):
        from ..adapters.filesystem_publication import FilesystemAtomicPublicationStore

        return FilesystemAtomicPublicationStore(*args, **kwargs)
