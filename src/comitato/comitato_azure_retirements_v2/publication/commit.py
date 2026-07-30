from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .model import PublicationCandidate
from .staging import PublicationError, StagedGeneration, stage_candidate


@dataclass(frozen=True, slots=True)
class PublicationReceipt:
    generation: str
    current_reference: str


class AtomicFilesystemPublicationStore:
    def __init__(self, destination: Path, *, fail_before_switch: bool = False) -> None:
        self.destination = destination
        self.fail_before_switch = fail_before_switch

    def stage(self, candidate: PublicationCandidate) -> StagedGeneration:
        return stage_candidate(candidate, self.destination)

    def commit(self, generation: StagedGeneration) -> PublicationReceipt:
        if self.fail_before_switch:
            raise PublicationError("fault injected before atomic current switch")
        generations = self.destination / "generations"
        generations.mkdir(parents=True, exist_ok=True)
        final_generation = generations / generation.generation_dir.name
        os.replace(generation.generation_dir, final_generation)
        reference = f"generations/{final_generation.name}\n"
        temporary_reference = self.destination / f".current-{final_generation.name}.tmp"
        with temporary_reference.open("w", encoding="utf-8") as handle:
            handle.write(reference)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_reference, self.destination / "current")
        return PublicationReceipt(
            generation=final_generation.name,
            current_reference=reference.strip(),
        )


def read_current_tree(destination: Path) -> dict[str, bytes]:
    reference = (destination / "current").read_text(encoding="utf-8").strip()
    current = destination / reference
    return {
        path.relative_to(current).as_posix(): path.read_bytes()
        for path in sorted(current.rglob("*"))
        if path.is_file()
    }
