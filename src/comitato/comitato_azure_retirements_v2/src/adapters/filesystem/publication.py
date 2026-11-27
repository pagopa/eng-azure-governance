from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from ...domain.diagnostics import Diagnostic
from ...ports import NullRunObserver, RunObserver, RuntimeEvent
from ...publication.model import (
    PublicationCandidate,
    PublicationError,
    PublicationReceipt,
)
from .staging import ValidatedStagedGeneration, stage_candidate


@dataclass(slots=True)
class _Replacement:
    name: str
    staged: Path
    destination: Path
    root: Path
    backup_started: bool = False
    switch_started: bool = False

    @property
    def backup(self) -> Path:
        return self.staged.with_name(f"{self.staged.name}-previous")


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
            return self._commit(candidate, generation)
        finally:
            self._discard_unpublished(generation)

    def _discard_unpublished(self, generation: ValidatedStagedGeneration) -> None:
        for generation_dir, staging_root in (
            (generation.generation_dir, self.destination / ".staging"),
            (
                generation.support_generation_dir,
                self.support_destination / ".staging",
            ),
        ):
            try:
                generation_dir.relative_to(staging_root)
            except ValueError:
                continue
            shutil.rmtree(generation_dir, ignore_errors=True)

    def _preflight(self, run_id: str) -> None:
        self._observer.emit(
            RuntimeEvent(
                "INFO",
                "publication_preflight",
                "Publication preflight checked",
                run_id,
            )
        )
        try:
            if self.support_destination == self.destination:
                raise OSError(
                    "support destination collides with publication destination"
                )
            for root in (self.destination, self.support_destination):
                staging_root = root / ".staging"
                staging_root.mkdir(parents=True, exist_ok=True)
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
        self._observer.emit(
            RuntimeEvent(
                "INFO",
                "publication_staging_started",
                "Publication staging started",
                candidate.context.run_id,
                {"artifacts": len(candidate.artifacts)},
            )
        )
        self._preflight(candidate.context.run_id)
        generation = stage_candidate(
            candidate,
            self.destination,
            self.support_destination,
            fault_injector=lambda point, artifact: self._inject_fault(
                candidate, point, artifact
            ),
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

    def _inject_fault(
        self, candidate: PublicationCandidate, point: str, artifact: str = ""
    ) -> None:
        pass

    def _commit(
        self, candidate: PublicationCandidate, generation: ValidatedStagedGeneration
    ) -> PublicationReceipt:
        self._inject_fault(candidate, "before_switch")
        self._preflight(candidate.context.run_id)
        if self.fail_before_switch:
            raise PublicationError("fault injected before monthly publication switch")
        as_of = candidate.context.as_of_date
        month_reference = f"{as_of.year:04d}/{as_of.month:02d}"
        replacements = (
            _Replacement(
                "export",
                generation.generation_dir,
                self.destination / month_reference,
                self.destination,
            ),
            _Replacement(
                "support",
                generation.support_generation_dir,
                self.support_destination / month_reference,
                self.support_destination,
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
        committed = False
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
            for replacement in replacements:
                destination = replacement.destination
                backup = replacement.backup
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists() and not destination.is_dir():
                    raise OSError("monthly publication path is not a directory")
                if backup.exists():
                    raise OSError("monthly publication backup already exists")
                if destination.exists():
                    replacement.backup_started = True
                    os.replace(destination, backup)
                self._inject_fault(candidate, f"after_{replacement.name}_backup")
            for replacement in replacements:
                replacement.switch_started = True
                os.replace(replacement.staged, replacement.destination)
                self._inject_fault(candidate, f"after_{replacement.name}_switch")
            self._inject_fault(candidate, "durable_marker")
            if candidate.after_switch is not None:
                candidate.after_switch()
            committed = True
        except OSError as exc:
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
        finally:
            if not committed:
                for replacement in reversed(replacements):
                    # An interruption can arrive after rename but before it returns.
                    if replacement.switch_started and not replacement.staged.exists():
                        shutil.rmtree(replacement.destination, ignore_errors=True)
                    if replacement.backup_started and replacement.backup.exists():
                        try:
                            os.replace(replacement.backup, replacement.destination)
                        except OSError:
                            self._warnings.append(
                                "superseded monthly bundle restoration failed"
                            )

        for replacement in replacements:
            if replacement.backup_started:
                try:
                    if replacement.name == "export":
                        self._inject_fault(candidate, "cleanup")
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
        super().__init__(destination, support_destination, observer=observer)
        self.fault = fault
        self.candidates: list[PublicationCandidate] = []

    def publish(self, candidate: PublicationCandidate) -> PublicationReceipt:
        self.candidates.append(candidate)
        return super().publish(candidate)

    def _inject_fault(
        self, candidate: PublicationCandidate, point: str, artifact: str = ""
    ) -> None:
        if point != self.fault:
            return
        if point == "cleanup":
            raise OSError("filesystem cleanup failed")
        stage = "staging" if artifact else "commit"
        timing = "before" if artifact or point == "before_switch" else "during"
        raise PublicationError(
            Diagnostic(
                severity="error",
                code=f"filesystem_{point}_failure",
                stage=stage,
                report=candidate.context.request.selector.value,
                run_id=candidate.context.run_id,
                artifact=artifact or "publication-manifest.json",
                message=f"filesystem {point} failed {timing} publication switch",
            )
        )
