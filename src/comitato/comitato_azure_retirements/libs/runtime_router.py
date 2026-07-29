"""Workflow routing plan for Azure retirements runtime execution."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

_KNOWN_WORKFLOWS = ("raw", "aggregate", "slide")


class StageAction(str, Enum):
    """Represents how a stage should be handled by the runtime pipeline."""

    EXECUTE = "execute"
    REUSE = "reuse"
    SKIP = "skip"


@dataclass(frozen=True)
class RuntimeRoute:
    """Concrete workflow actions resolved from the selected workflow list."""

    selected_workflows: tuple[str, ...]
    raw_action: StageAction
    aggregate_action: StageAction
    slide_action: StageAction

    @property
    def name(self) -> str:
        return "+".join(self.selected_workflows)

    def describe(self) -> str:
        return (
            f"raw={self.raw_action.value}, "
            f"aggregate={self.aggregate_action.value}, "
            f"slide={self.slide_action.value}"
        )


def build_runtime_route(workflows: Sequence[str]) -> RuntimeRoute:
    """Build a deterministic runtime route from validated workflow inputs."""

    requested = {workflow.strip().lower() for workflow in workflows if workflow.strip()}
    unknown = sorted(requested.difference(_KNOWN_WORKFLOWS))
    if unknown:
        raise ValueError(f"Unsupported workflow value(s): {', '.join(unknown)}")

    if not requested:
        raise ValueError("At least one workflow must be selected")

    selected_workflows = tuple(
        workflow for workflow in _KNOWN_WORKFLOWS if workflow in requested
    )
    raw_action = (
        StageAction.EXECUTE
        if "raw" in requested
        else StageAction.REUSE
        if "aggregate" in requested
        else StageAction.SKIP
    )
    aggregate_action = (
        StageAction.EXECUTE
        if "aggregate" in requested
        else StageAction.REUSE
        if "slide" in requested
        else StageAction.SKIP
    )
    slide_action = StageAction.EXECUTE if "slide" in requested else StageAction.SKIP

    return RuntimeRoute(
        selected_workflows=selected_workflows,
        raw_action=raw_action,
        aggregate_action=aggregate_action,
        slide_action=slide_action,
    )
