"""Versioned v2 report contracts."""

from .advisor_v1 import ADVISOR_V1
from .aggregate_v1 import AGGREGATE_V1
from .service_health_v1 import SERVICE_HEALTH_V1
from .slides_v1 import SLIDES_V1

ALL_V1_CONTRACTS = (ADVISOR_V1, SERVICE_HEALTH_V1, AGGREGATE_V1, SLIDES_V1)
RAW_V1_CONTRACTS = (ADVISOR_V1, SERVICE_HEALTH_V1)

__all__ = [
    "ADVISOR_V1",
    "AGGREGATE_V1",
    "SERVICE_HEALTH_V1",
    "SLIDES_V1",
    "ALL_V1_CONTRACTS",
    "RAW_V1_CONTRACTS",
]
