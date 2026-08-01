from __future__ import annotations

from dataclasses import dataclass

from ..contracts import AGGREGATE_V1, SLIDES_V1
from ..domain.execution import ReportSelector
from .advisor import ADVISOR_REPORT
from .model import ReportDefinition
from .service_health import SERVICE_HEALTH_REPORT


@dataclass(frozen=True, slots=True)
class SelectedReportClosure:
    selector: ReportSelector
    stages: tuple[str, ...]
    required: tuple[ReportDefinition, ...]
    published: tuple[ReportDefinition, ...]
    path_owners: tuple[tuple[str, ReportDefinition], ...]

    def requires(self, selector: ReportSelector) -> bool:
        return any(item.selector is selector for item in self.required)

    def publishes(self, selector: ReportSelector) -> bool:
        return any(item.selector is selector for item in self.published)

    @property
    def expected_paths(self) -> tuple[str, ...]:
        return tuple(path for item in self.published for path in item.paths)

    @property
    def all_paths(self) -> tuple[str, ...]:
        return tuple(path for path, _ in self.path_owners)

    def owner_of(self, path: str) -> ReportDefinition:
        for owned_path, definition in self.path_owners:
            if owned_path == path:
                return definition
        raise KeyError(f"no report owns path: {path}")


class ReportCatalog:
    def __init__(self, definitions: tuple[ReportDefinition, ...]) -> None:
        selectors = tuple(item.selector for item in definitions)
        if len(selectors) != len(set(selectors)):
            raise ValueError("report selectors must be unique")
        paths = tuple(path for item in definitions for path in item.paths)
        if len(paths) != len(set(paths)):
            raise ValueError("report paths must be unique")
        self._definitions = definitions
        self._by_selector = {item.selector: item for item in definitions}
        self._by_path = {
            path: item for item in definitions for path in item.paths
        }

    @property
    def all_paths(self) -> tuple[str, ...]:
        return tuple(path for item in self._definitions for path in item.paths)

    def owner_of(self, path: str) -> ReportDefinition:
        try:
            return self._by_path[path]
        except KeyError as exc:
            raise KeyError(f"no report owns path: {path}") from exc

    def plan(self, selector: ReportSelector) -> SelectedReportClosure:
        roots = (
            self._definitions
            if selector is ReportSelector.ALL
            else (self._by_selector[selector],)
        )
        required: list[ReportDefinition] = []
        visited: set[ReportSelector] = set()

        def visit(current: ReportDefinition) -> None:
            if current.selector in visited:
                return
            for dependency in current.dependencies:
                visit(self._by_selector[dependency])
            visited.add(current.selector)
            required.append(current)

        for root in roots:
            visit(root)

        stages = ("scope", "catalog") + tuple(
            item.stage for item in required
        ) + ("publication",)
        published = tuple(
            item for item in roots if item.selector is not ReportSelector.ALL
        )
        if selector is ReportSelector.ALL:
            published = tuple(roots)
        path_owners = tuple(
            (path, definition)
            for definition in self._definitions
            for path in definition.paths
        )
        return SelectedReportClosure(
            selector,
            stages,
            tuple(required),
            published,
            path_owners,
        )


DEFAULT_REPORT_CATALOG = ReportCatalog(
    (
        ReportDefinition(
            ReportSelector.ADVISOR,
            "advisor",
            "advisor",
            (),
            ADVISOR_REPORT.contract,
        ),
        ReportDefinition(
            ReportSelector.SERVICE_HEALTH,
            "service-health",
            "service-health",
            (),
            SERVICE_HEALTH_REPORT.contract,
        ),
        ReportDefinition(
            ReportSelector.AGGREGATE,
            "aggregate",
            "aggregate",
            (ReportSelector.ADVISOR, ReportSelector.SERVICE_HEALTH),
            AGGREGATE_V1,
        ),
        ReportDefinition(
            ReportSelector.SLIDES,
            "slides",
            "slides",
            (ReportSelector.AGGREGATE,),
            SLIDES_V1,
        ),
    )
)


ReportPlan = SelectedReportClosure


__all__ = [
    "DEFAULT_REPORT_CATALOG",
    "ReportCatalog",
    "ReportPlan",
    "SelectedReportClosure",
]
