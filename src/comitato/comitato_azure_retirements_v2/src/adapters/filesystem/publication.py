from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ...domain.diagnostics import Diagnostic
from ...ports import NullRunObserver, RunObserver, RuntimeEvent
from ...publication.model import (
    PublicationCandidate,
    PublicationError,
    PublicationReceipt,
)
from .staging import ValidatedStagedGeneration, stage_candidate

_COMMIT_FAULTS = {
    "before_switch",
    "after_export_backup",
    "after_export_switch",
    "after_support_backup",
    "after_support_switch",
    "durable_marker",
}


@dataclass(slots=True)
class PublicationReplacement:
    staged: Path
    destination: Path
    backup: Path
    root: Path
    previous_moved: bool = False
    new_moved: bool = False


class FilesystemAtomicPublicationStore:
    """Publish one validated, replaceable bundle for the candidate's month."""

    def __init__(
        self,
        destination: Path,
        support_destination: Path | None = None,
        *,
        fail_before_switch: bool = False,
        observer: RunObserver | None = None,
    ) -> None:
        self.destination = destination.resolve()
        self.support_destination = (
            support_destination.resolve()
            if support_destination is not None
            else destination.with_name(f"{destination.name}-support").resolve()
        )
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

    def _discard_unpublished(self, generation: ValidatedStagedGeneration) -> None:
        for generation_dir, staging_root in (
            (Path(generation.generation_dir), self.destination / ".staging"),
            (
                Path(generation.support_generation_dir),
                self.support_destination / ".staging",
            ),
        ):
            try:
                generation_dir.relative_to(staging_root)
            except ValueError:
                continue
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
            self.support_destination.mkdir(parents=True, exist_ok=True)
            if not self.support_destination.is_dir():
                raise OSError("support destination is not a directory")
            if self.support_destination == self.destination:
                raise OSError("support destination collides with publication destination")
            for root in (self.destination, self.support_destination):
                staging_root = root / ".staging"
                staging_root.mkdir(exist_ok=True)
                if staging_root.stat().st_dev != root.stat().st_dev:
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

    def _stage(self, candidate: PublicationCandidate) -> ValidatedStagedGeneration:
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
        generation = stage_candidate(
            candidate, self.destination, self.support_destination
        )
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

    def _inject_commit_fault(self, point: str) -> None:
        return None

    def _commit(self, generation: ValidatedStagedGeneration) -> PublicationReceipt:
        self._preflight()
        if self.fail_before_switch:
            raise PublicationError("fault injected before monthly publication switch")
        candidate = getattr(self, "_candidate", None)
        if candidate is None:
            raise PublicationError(
                Diagnostic(
                    "error",
                    "missing_publication_candidate",
                    "commit",
                    "",
                    "",
                    message="publication candidate is unavailable",
                )
            )
        month_reference = f"{candidate.context.as_of_date.year:04d}/{candidate.context.as_of_date.month:02d}"
        monthly_bundle = self.destination / month_reference
        monthly_support = self.support_destination / month_reference
        replacements = (
            PublicationReplacement(
                staged=Path(generation.generation_dir),
                destination=monthly_bundle,
                backup=self.destination
                / ".staging"
                / f"{Path(generation.generation_dir).name}-previous",
                root=self.destination,
            ),
            PublicationReplacement(
                staged=Path(generation.support_generation_dir),
                destination=monthly_support,
                backup=self.support_destination
                / ".staging"
                / f"{Path(generation.support_generation_dir).name}-previous",
                root=self.support_destination,
            ),
        )
        for replacement in replacements:
            staged = replacement.staged
            root = replacement.root
            try:
                staged.relative_to(root / ".staging")
            except ValueError as exc:
                raise PublicationError(
                    Diagnostic(
                        "error",
                        "unsafe_staged_generation",
                        "commit",
                        "",
                        "",
                        message="staged generation is outside the private staging area",
                    )
                ) from exc
            if staged.stat().st_dev != root.stat().st_dev:
                raise PublicationError(
                    Diagnostic(
                        "error",
                        "cross_device_publication",
                        "commit",
                        "",
                        "",
                        message=(
                            "publication generation is not on the destination filesystem"
                        ),
                    )
                )
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
            for index, replacement in enumerate(replacements):
                destination = replacement.destination
                backup = replacement.backup
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists() and not destination.is_dir():
                    raise OSError("monthly publication path is not a directory")
                if backup.exists():
                    raise OSError("monthly publication backup already exists")
                if destination.exists():
                    os.replace(destination, backup)
                    replacement.previous_moved = True
                self._inject_commit_fault(
                    "after_export_backup" if index == 0 else "after_support_backup"
                )
            for index, replacement in enumerate(replacements):
                os.replace(replacement.staged, replacement.destination)
                replacement.new_moved = True
                self._inject_commit_fault(
                    "after_export_switch" if index == 0 else "after_support_switch"
                )
            self._inject_commit_fault("durable_marker")
            if candidate.after_switch is not None:
                candidate.after_switch()
        except (OSError, PublicationError) as exc:
            for replacement in reversed(replacements):
                if replacement.new_moved:
                    shutil.rmtree(replacement.destination, ignore_errors=True)
                if (
                    replacement.previous_moved
                    and replacement.backup.exists()
                ):
                    try:
                        os.replace(replacement.backup, replacement.destination)
                    except OSError:
                        self._warnings.append(
                            "superseded monthly bundle restoration failed"
                        )
                shutil.rmtree(replacement.staged, ignore_errors=True)
            if isinstance(exc, PublicationError):
                raise
            raise PublicationError(
                Diagnostic(
                    "error",
                    "commit_failure",
                    "commit",
                    "",
                    "",
                    message="monthly publication replacement failed",
                )
            ) from exc

        for replacement in replacements:
            if replacement.previous_moved:
                try:
                    shutil.rmtree(replacement.backup)
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
        support_destination: Path | None = None,
        *,
        fault: str,
        observer: RunObserver | None = None,
    ) -> None:
        super().__init__(
            destination, support_destination, observer=observer
        )
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

        generation = stage_candidate(
            candidate,
            self.destination,
            self.support_destination,
            fault_injector=inject,
        )
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

    def _commit(self, generation: ValidatedStagedGeneration) -> PublicationReceipt:
        if self.fault == "before_switch":
            candidate = getattr(self, "_candidate", None)
            report = getattr(getattr(candidate, "context", None), "request", None)
            report_name = (
                getattr(report, "selector", "").value
                if getattr(report, "selector", None)
                else ""
            )
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

    def _inject_commit_fault(self, point: str) -> None:
        if point not in _COMMIT_FAULTS or point != self.fault:
            return
        candidate = getattr(self, "_candidate", None)
        report = getattr(getattr(candidate, "context", None), "request", None)
        report_name = (
            getattr(report, "selector", "").value
            if getattr(report, "selector", None)
            else ""
        )
        run_id = getattr(getattr(candidate, "context", None), "run_id", "")
        raise PublicationError(
            Diagnostic(
                severity="error",
                code=f"filesystem_{point}_failure",
                stage="commit",
                report=report_name,
                run_id=run_id,
                artifact="publication-manifest.json",
                message=f"filesystem {point} failed during publication switch",
            )
        )
