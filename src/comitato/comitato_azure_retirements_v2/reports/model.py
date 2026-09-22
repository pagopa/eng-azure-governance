from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import json
from typing import Any

from ..acquisition.model import SourceAcquisition
from ..contracts._base import TsvContract
from ..contracts.model import Artifact, EncodedArtifact
from ..domain.execution import ReportSelector


@dataclass(frozen=True, slots=True)
class PreparedRawReport:
    acquisition: SourceAcquisition
    artifact: Artifact[Mapping[str, str]]
    artifacts: tuple[EncodedArtifact, EncodedArtifact]


class StagedDecodeFailure(ValueError):
    def __init__(self, logical_path: str) -> None:
        self.logical_path = logical_path
        super().__init__(logical_path)


@dataclass(frozen=True, slots=True)
class ReportDefinition:
    selector: ReportSelector
    name: str
    stage: str
    dependencies: tuple[ReportSelector, ...]
    contract: TsvContract[Any]
    sidecar_contracts: tuple[Any, ...] = ()

    @property
    def paths(self) -> tuple[str, ...]:
        companion = self.contract.companion_path
        return (
            (self.contract.path,)
            + ((companion,) if companion else ())
            + tuple(item.path for item in self.sidecar_contracts)
        )

    def verify_staged_artifact(
        self,
        logical_path: str,
        payloads: Mapping[str, bytes],
        context,
    ) -> tuple:
        try:
            for sidecar in self.sidecar_contracts:
                if logical_path == sidecar.path:
                    return sidecar.verify_staged_artifact(logical_path, payloads, context)
            if logical_path == self.contract.path:
                decoded = self.contract.decode(payloads[logical_path])
                companion_records = decoded.companion_records
                companion_path = self.contract.companion_path
                if companion_path:
                    companion_data = payloads.get(companion_path)
                    if companion_data is not None:
                        decoded_companions = self.contract.decode_companion(companion_data)
                        companion_records = tuple(
                            item
                            for item in decoded_companions
                            if not isinstance(item, Mapping)
                            or item.get("kind") != "observation_accounting"
                        )
                        accounting = tuple(
                            item
                            for item in decoded_companions
                            if isinstance(item, Mapping)
                            and item.get("kind") == "observation_accounting"
                        )
                    else:
                        accounting = decoded.accounting
                else:
                    accounting = decoded.accounting
                decoded = Artifact(
                    contract=decoded.contract,
                    schema_version=decoded.schema_version,
                    run_id=decoded.run_id or context.run_id,
                    records=decoded.records,
                    companion_records=companion_records,
                    accounting=accounting,
                )
                result = self.contract.validate(decoded, context)
                return result.diagnostics if not result.is_valid else ()
            if logical_path == self.contract.companion_path:
                self.contract.decode_companion(payloads[logical_path])
                return ()
            raise ValueError(f"path is not owned by {self.name}: {logical_path}")
        except (UnicodeError, ValueError, TypeError, json.JSONDecodeError) as exc:
            raise StagedDecodeFailure(logical_path) from exc
