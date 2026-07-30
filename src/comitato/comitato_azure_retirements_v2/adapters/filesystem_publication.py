from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from ..domain.diagnostics import Diagnostic
from ..publication.commit import PublicationReceipt
from ..publication.staging import PublicationError, stage_candidate


_COMMIT_FAULTS = {"before_switch", "durable_marker"}


class FilesystemAtomicPublicationStore:
    """Publish a validated generation through one atomic current-reference switch."""

    def __init__(self, destination: Path, *, fail_before_switch: bool = False) -> None:
        self.destination = destination
        self.fail_before_switch = fail_before_switch
        self._warnings: list[str] = []

    @property
    def warnings(self) -> tuple[str, ...]:
        return tuple(self._warnings)

    def preflight(self) -> None:
        try:
            self.destination.mkdir(parents=True, exist_ok=True)
            if not self.destination.is_dir():
                raise OSError("destination is not a directory")
            (self.destination / ".staging").mkdir(exist_ok=True)
            (self.destination / "generations").mkdir(exist_ok=True)
            if (self.destination / "current").exists() and not (self.destination / "current").is_file():
                raise OSError("current reference is not a file")
            if (self.destination / ".staging").stat().st_dev != self.destination.stat().st_dev:
                raise OSError("staging is on a different filesystem")
            if (self.destination / "generations").stat().st_dev != self.destination.stat().st_dev:
                raise OSError("generations are on a different filesystem")
        except OSError as exc:
            diagnostic = Diagnostic(
                severity="error",
                code="publication_destination_unavailable",
                stage="commit",
                report="",
                run_id="",
                message="publication destination cannot prove same-filesystem atomic capability",
            )
            raise PublicationError(diagnostic) from exc

    def stage(self, candidate: Any):
        self.preflight()
        self._candidate = candidate
        return stage_candidate(candidate, self.destination)

    def commit(self, generation: Any) -> PublicationReceipt:
        self.preflight()
        if self.fail_before_switch:
            raise PublicationError("fault injected before atomic current switch")
        generation_dir = Path(generation.generation_dir)
        staging_root = self.destination / ".staging"
        try:
            generation_dir.relative_to(staging_root)
        except ValueError as exc:
            raise PublicationError(
                Diagnostic("error", "unsafe_staged_generation", "commit", "", "", message="staged generation is outside the private staging area")
            ) from exc
        if generation_dir.stat().st_dev != self.destination.stat().st_dev:
            raise PublicationError(
                Diagnostic("error", "cross_device_publication", "commit", "", "", message="publication generation is not on the destination filesystem")
            )

        old_reference = self._read_reference()
        final_generation = self.destination / "generations" / generation_dir.name
        temporary_reference = self.destination / f".current-{generation_dir.name}.tmp"
        try:
            os.replace(generation_dir, final_generation)
            reference = f"generations/{final_generation.name}\n"
            if temporary_reference.exists():
                temporary_reference.unlink()
            with temporary_reference.open("wb") as handle:
                handle.write(reference.encode("utf-8"))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_reference, self.destination / "current")
        except OSError as exc:
            temporary_reference.unlink(missing_ok=True)
            shutil.rmtree(final_generation, ignore_errors=True)
            raise PublicationError(
                Diagnostic("error", "commit_failure", "commit", "", "", message="atomic publication switch failed")
            ) from exc

        if old_reference:
            old_generation = self.destination / old_reference
            try:
                shutil.rmtree(old_generation)
            except OSError:
                self._warnings.append("superseded generation cleanup failed")
        return PublicationReceipt(
            generation=final_generation.name,
            current_reference=reference.strip(),
        )

    def _read_reference(self) -> str:
        current = self.destination / "current"
        if not current.exists():
            return ""
        value = current.read_text(encoding="utf-8").strip()
        if not value or not value.startswith("generations/") or ".." in Path(value).parts:
            raise PublicationError(
                Diagnostic("error", "invalid_current_reference", "commit", "", "", message="current publication reference is invalid")
            )
        return value


class FaultInjectingPublicationStore(FilesystemAtomicPublicationStore):
    """Test-only store that fails at one named pre-commit capability boundary."""

    def __init__(self, destination: Path, *, fault: str) -> None:
        super().__init__(destination)
        self.fault = fault
        self.candidates: list[Any] = []

    def stage(self, candidate: Any):
        self.preflight()
        self._candidate = candidate
        self.candidates.append(candidate)

        def inject(point: str, artifact: str) -> None:
            if point == self.fault:
                raise PublicationError(
                    Diagnostic(
                        severity="error",
                        code=f"filesystem_{point}_failure",
                        stage="staging",
                        report=candidate.context.request.selector.value,
                        run_id=candidate.context.run_id,
                        artifact=artifact,
                        message=f"filesystem {point} failed before publication switch",
                    )
                )

        return stage_candidate(candidate, self.destination, fault_injector=inject)

    def commit(self, generation: Any) -> PublicationReceipt:
        if self.fault in _COMMIT_FAULTS:
            candidate = getattr(self, "_candidate", None)
            report = getattr(getattr(candidate, "context", None), "request", None)
            report_name = getattr(report, "selector", "").value if getattr(report, "selector", None) else ""
            run_id = getattr(getattr(candidate, "context", None), "run_id", "")
            raise PublicationError(
                Diagnostic(
                    severity="error",
                    code=f"filesystem_{self.fault}_failure",
                    stage="commit",
                    report=report_name,
                    run_id=run_id,
                    artifact="publication-manifest.json",
                    message=f"filesystem {self.fault} failed before publication switch",
                )
            )
        if self.fault == "cleanup":
            old_reference = self._read_reference()
            receipt = super().commit(generation)
            if old_reference:
                self._warnings.append("superseded generation cleanup failed")
            return receipt
        return super().commit(generation)
