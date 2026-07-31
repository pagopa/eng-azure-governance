from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from ..domain.diagnostics import Diagnostic
from ..publication.model import (
    PublicationCandidate,
    PublicationError,
    PublicationReceipt,
)
from ..ports import NullRunObserver, RunObserver, RuntimeEvent
from .filesystem_staging import _ValidatedStagedGeneration, stage_candidate


_COMMIT_FAULTS = {"before_switch", "durable_marker"}


class FilesystemAtomicPublicationStore:
    """Publish one validated, replaceable bundle for the candidate's month."""

    def __init__(
        self,
        destination: Path,
        *,
        fail_before_switch: bool = False,
        observer: RunObserver | None = None,
    ) -> None:
        self.destination = destination
        self.fail_before_switch = fail_before_switch
        self._warnings: list[str] = []
        self._observer = observer or NullRunObserver()

    @property
    def warnings(self) -> tuple[str, ...]:
        return tuple(self._warnings)

    def publish(self, candidate: PublicationCandidate) -> PublicationReceipt:
        generation = self._stage(candidate)
        try:
            return self._commit(generation)
        except Exception:
            self._discard_unpublished(generation)
            raise

    def _discard_unpublished(self, generation: _ValidatedStagedGeneration) -> None:
        generation_dir = Path(generation.generation_dir)
        staging_root = self.destination / ".staging"
        try:
            generation_dir.relative_to(staging_root)
        except ValueError:
            return
        shutil.rmtree(generation_dir, ignore_errors=True)

    def _preflight(self) -> None:
        candidate = getattr(self, "_candidate", None)
        run_id = getattr(getattr(candidate, "context", None), "run_id", "")
        self._observer.emit(
            RuntimeEvent(
                "INFO",
                "publication_preflight",
                "Publication preflight checked",
                run_id,
            )
        )
        try:
            self.destination.mkdir(parents=True, exist_ok=True)
            if not self.destination.is_dir():
                raise OSError("destination is not a directory")
            staging_root = self.destination / ".staging"
            staging_root.mkdir(exist_ok=True)
            if staging_root.stat().st_dev != self.destination.stat().st_dev:
                raise OSError("staging is on a different filesystem")
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

    def _stage(self, candidate: PublicationCandidate) -> _ValidatedStagedGeneration:
        self._candidate = candidate
        self._observer.emit(
            RuntimeEvent(
                "INFO",
                "publication_staging_started",
                "Publication staging started",
                candidate.context.run_id,
                {"artifacts": len(candidate.artifacts)},
            )
        )
        self._preflight()
        generation = stage_candidate(candidate, self.destination)
        self._observer.emit(
            RuntimeEvent(
                "INFO",
                "publication_staging_completed",
                "Publication staging completed",
                candidate.context.run_id,
                {
                    "artifacts": len(generation.artifacts),
                    "bytes": sum(artifact.bytes for artifact in generation.artifacts),
                },
            )
        )
        return generation

    def _commit(self, generation: _ValidatedStagedGeneration) -> PublicationReceipt:
        self._preflight()
        if self.fail_before_switch:
            raise PublicationError("fault injected before monthly publication switch")
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

        candidate = getattr(self, "_candidate", None)
        if candidate is None:
            raise PublicationError(
                Diagnostic("error", "missing_publication_candidate", "commit", "", "", message="publication candidate is unavailable")
            )
        month_reference = f"{candidate.context.as_of_date.year:04d}/{candidate.context.as_of_date.month:02d}"
        monthly_bundle = self.destination / month_reference
        backup_bundle = self.destination / ".staging" / f"{generation_dir.name}-previous"
        previous_bundle_moved = False
        new_bundle_moved = False
        try:
            self._observer.emit(
                RuntimeEvent(
                    "INFO",
                    "publication_switch_started",
                    "Publication switch started",
                    candidate.context.run_id,
                    {"current_reference": month_reference},
                )
            )
            monthly_bundle.parent.mkdir(parents=True, exist_ok=True)
            if monthly_bundle.exists() and not monthly_bundle.is_dir():
                raise OSError("monthly publication path is not a directory")
            if backup_bundle.exists():
                raise OSError("monthly publication backup already exists")
            if monthly_bundle.exists():
                os.replace(monthly_bundle, backup_bundle)
                previous_bundle_moved = True
            os.replace(generation_dir, monthly_bundle)
            new_bundle_moved = True
        except OSError as exc:
            if new_bundle_moved:
                shutil.rmtree(monthly_bundle, ignore_errors=True)
            if previous_bundle_moved and backup_bundle.exists():
                try:
                    os.replace(backup_bundle, monthly_bundle)
                except OSError:
                    self._warnings.append("superseded monthly bundle restoration failed")
            shutil.rmtree(generation_dir, ignore_errors=True)
            raise PublicationError(
                Diagnostic("error", "commit_failure", "commit", "", "", message="monthly publication replacement failed")
            ) from exc

        if previous_bundle_moved:
            try:
                shutil.rmtree(backup_bundle)
            except OSError:
                self._warnings.append("superseded monthly bundle cleanup failed")
                self._observer.emit(
                    RuntimeEvent(
                        "WARNING",
                        "publication_cleanup_warning",
                        "Superseded monthly bundle cleanup failed",
                        candidate.context.run_id,
                    )
                )
        receipt = PublicationReceipt(
            generation=month_reference,
            current_reference=month_reference,
        )
        self._observer.emit(
            RuntimeEvent(
                "INFO",
                "publication_completed",
                "Publication completed",
                candidate.context.run_id,
                {"current_reference": receipt.current_reference},
            )
        )
        return receipt


class FaultInjectingPublicationStore(FilesystemAtomicPublicationStore):
    """Test-only store that fails at one named pre-commit capability boundary."""

    def __init__(
        self,
        destination: Path,
        *,
        fault: str,
        observer: RunObserver | None = None,
    ) -> None:
        super().__init__(destination, observer=observer)
        self.fault = fault
        self.candidates: list[Any] = []

    def _stage(self, candidate: PublicationCandidate):
        self._candidate = candidate
        self._observer.emit(
            RuntimeEvent(
                "INFO",
                "publication_staging_started",
                "Publication staging started",
                candidate.context.run_id,
                {"artifacts": len(candidate.artifacts)},
            )
        )
        self._preflight()
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

        generation = stage_candidate(candidate, self.destination, fault_injector=inject)
        self._observer.emit(
            RuntimeEvent(
                "INFO",
                "publication_staging_completed",
                "Publication staging completed",
                candidate.context.run_id,
                {
                    "artifacts": len(generation.artifacts),
                    "bytes": sum(artifact.bytes for artifact in generation.artifacts),
                },
            )
        )
        return generation

    def _commit(self, generation: _ValidatedStagedGeneration) -> PublicationReceipt:
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
            candidate = getattr(self, "_candidate", None)
            had_previous_bundle = False
            if candidate is not None:
                month_reference = f"{candidate.context.as_of_date.year:04d}/{candidate.context.as_of_date.month:02d}"
                had_previous_bundle = (self.destination / month_reference).exists()
            receipt = super()._commit(generation)
            if had_previous_bundle:
                self._warnings.append("superseded monthly bundle cleanup failed")
                self._observer.emit(
                    RuntimeEvent(
                        "WARNING",
                        "publication_cleanup_warning",
                        "Superseded monthly bundle cleanup failed",
                        candidate.context.run_id,
                    )
                )
            return receipt
        return super()._commit(generation)
