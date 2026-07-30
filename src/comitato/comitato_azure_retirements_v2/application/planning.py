from __future__ import annotations

from ..domain.execution import DependencyPlan, ReportSelector


SELECTED_PATHS = {
    ReportSelector.ALL: (
        "01_azure_advisor_retirements_raw.tsv",
        "01_azure_advisor_retirements_raw.jsonl",
        "01_azure_service_health_advisories_raw.tsv",
        "01_azure_service_health_advisories_raw.jsonl",
        "02_azure_retirements_aggregate.tsv",
        "03_azure_retirements_slide.tsv",
    ),
    ReportSelector.ADVISOR: (
        "01_azure_advisor_retirements_raw.tsv",
        "01_azure_advisor_retirements_raw.jsonl",
    ),
    ReportSelector.SERVICE_HEALTH: (
        "01_azure_service_health_advisories_raw.tsv",
        "01_azure_service_health_advisories_raw.jsonl",
    ),
    ReportSelector.AGGREGATE: ("02_azure_retirements_aggregate.tsv",),
    ReportSelector.SLIDES: ("03_azure_retirements_slide.tsv",),
}


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
    return DependencyPlan(stages=stages, selected_paths=SELECTED_PATHS[selector])
