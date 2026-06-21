"""Normalization compatibility wrapper for Advisor and Service Health rows."""

from __future__ import annotations

from .normalize_advisor import normalize_advisor_rows
from .normalize_service_health import normalize_service_health_rows

__all__ = ["normalize_advisor_rows", "normalize_service_health_rows"]
