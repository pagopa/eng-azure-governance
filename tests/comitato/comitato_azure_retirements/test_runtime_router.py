from __future__ import annotations

import pytest

from src.comitato.comitato_azure_retirements.libs.runtime_router import (
    StageAction,
    build_runtime_route,
)


@pytest.mark.parametrize(
    ("workflows", "expected_actions"),
    [
        (
            ["raw", "aggregate", "slide"],
            (StageAction.EXECUTE, StageAction.EXECUTE, StageAction.EXECUTE),
        ),
        (["raw"], (StageAction.EXECUTE, StageAction.SKIP, StageAction.SKIP)),
        (["aggregate"], (StageAction.REUSE, StageAction.EXECUTE, StageAction.SKIP)),
        (["slide"], (StageAction.SKIP, StageAction.REUSE, StageAction.EXECUTE)),
        (["raw", "slide"], (StageAction.EXECUTE, StageAction.REUSE, StageAction.EXECUTE)),
    ],
)
def test_build_runtime_route_assigns_stage_actions(
    workflows: list[str], expected_actions: tuple[StageAction, StageAction, StageAction]
) -> None:
    route = build_runtime_route(workflows)

    assert (
        route.raw_action,
        route.aggregate_action,
        route.slide_action,
    ) == expected_actions


def test_build_runtime_route_canonicalizes_selected_workflow_order() -> None:
    route = build_runtime_route(["slide", "raw", "slide"])

    assert route.selected_workflows == ("raw", "slide")
    assert route.name == "raw+slide"


def test_build_runtime_route_rejects_unknown_values() -> None:
    with pytest.raises(ValueError, match="Unsupported workflow"):
        build_runtime_route(["raw", "unknown"])
