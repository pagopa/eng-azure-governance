from __future__ import annotations

from ..domain.execution import DependencyPlan, ReportSelector


def build_dependency_plan(selector: ReportSelector) -> DependencyPlan:
    if selector is ReportSelector.ALL:
        stages = (
            "scope",
            "catalog",
            "advisor",
            "service-health",
            "aggregate",
            "slides",
            "publication",
        )
    elif selector is ReportSelector.ADVISOR:
        stages = ("scope", "catalog", "advisor", "publication")
    elif selector is ReportSelector.SERVICE_HEALTH:
        stages = ("scope", "catalog", "service-health", "publication")
    elif selector is ReportSelector.AGGREGATE:
        stages = (
            "scope",
            "catalog",
            "advisor",
            "service-health",
            "aggregate",
            "publication",
        )
    elif selector is ReportSelector.SLIDES:
        stages = (
            "scope",
            "catalog",
            "advisor",
            "service-health",
            "aggregate",
            "slides",
            "publication",
        )
    else:
        raise ValueError(f"unsupported report selector: {selector!r}")
    return DependencyPlan(stages=stages)
