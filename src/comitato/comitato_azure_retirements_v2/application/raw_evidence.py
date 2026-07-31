from typing import Literal

from ..acquisition.model import SourceAcquisition
from ..contracts import ADVISOR_V1, SERVICE_HEALTH_V1
from ..domain.evidence import AdvisorEnrichments, ServiceHealthSupplementalEvidence
from ..domain.execution import RunContext
from .advisor import normalize_advisor
from .orchestration_errors import ApplicationError, ContractValidationError
from .service_health import normalize_service_health


RawSourceName = Literal["advisor", "service-health"]


def prepare_raw_acquisition(
    source_name: RawSourceName,
    acquisition: SourceAcquisition,
    context: RunContext,
) -> SourceAcquisition:
    if not acquisition.receipt.is_complete:
        raise ApplicationError(f"incomplete {source_name} acquisition")
    if not acquisition.records:
        if acquisition.receipt.source_records != 0:
            raise ApplicationError(f"inconsistent {source_name} acquisition receipt")
        return acquisition
    if source_name == "advisor":
        result = normalize_advisor(acquisition, context, AdvisorEnrichments())
        contract = ADVISOR_V1
    else:
        result = normalize_service_health(
            acquisition,
            context,
            ServiceHealthSupplementalEvidence(),
        )
        contract = SERVICE_HEALTH_V1
    if not result.is_valid or result.value is None:
        raise ContractValidationError(
            result.diagnostics,
            f"invalid {source_name} raw contract",
        )
    artifact = result.value
    checked = contract.validate(artifact, context)
    if not checked.is_valid:
        raise ContractValidationError(
            checked.diagnostics,
            f"invalid {source_name} raw contract",
        )
    return SourceAcquisition(
        receipt=acquisition.receipt,
        records=artifact.records,
        companion_records=artifact.companion_records,
    )
