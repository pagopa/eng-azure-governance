"""Acquisition models and source boundaries."""
from .evidence import SourcePage, SourceRecord
from .paging import (
    AcquisitionIntegrityError,
    ScriptedRequest,
    collect_complete_pages,
)

__all__ = [
    "AcquisitionIntegrityError",
    "ScriptedRequest",
    "SourcePage",
    "SourceRecord",
    "collect_complete_pages",
]
