#!/usr/bin/env python3
"""Export Azure retirements into separated Advisor and Service Health aggregate TSV files."""

from __future__ import annotations

import sys
from pathlib import Path
from libs.config import parse_args
from libs.diagnostics import DiagnosticsCollector
from libs.runtime_live import live_mode
from libs.runtime_logging import ExecutionReporter
from libs.runtime_paths import (
    build_debug_log_path,
    build_output_dir,
    build_runtime_dir,
    scope_mode,
)
from libs.runtime_runner import run_export
from libs.runtime_stages import (
    add_live_empty_output_diagnostics,
    add_aggregate_contract_diagnostics,
    add_slide_source_link_diagnostics,
    diagnostic_summary,
    enforce_mandatory_raw_rows,
    fixture_mode,
    load_aggregate_stage_input,
    load_fixture,
    load_raw_stage_inputs,
    manifest_degraded_mode,
    schema_only,
)
from libs.tsv import write_json, write_jsonl, write_tsv

PLATFORMS_SOURCE_PATH = (
    Path(__file__).resolve().parents[2] / "_source_of_truth" / "platforms.yaml"
)
_schema_only = schema_only
_fixture_mode = fixture_mode
_live_mode = live_mode
_load_fixture = load_fixture
_load_raw_stage_inputs = load_raw_stage_inputs
_load_aggregate_stage_input = load_aggregate_stage_input
_enforce_mandatory_raw_rows = enforce_mandatory_raw_rows
_diagnostic_summary = diagnostic_summary
_manifest_degraded_mode = manifest_degraded_mode
_add_live_empty_output_diagnostics = add_live_empty_output_diagnostics
_add_aggregate_contract_diagnostics = add_aggregate_contract_diagnostics
_add_slide_source_link_diagnostics = add_slide_source_link_diagnostics


def _build_output_dir(root: Path, as_of_date) -> Path:
    return build_output_dir(root, as_of_date)


def _build_runtime_dir(as_of_date) -> Path:
    return build_runtime_dir(Path(__file__), as_of_date)


def _build_debug_log_path(runtime_dir: Path, run_id: str) -> Path:
    return build_debug_log_path(runtime_dir, run_id)


def _scope_mode(cfg):
    return scope_mode(cfg)


def main() -> int:
    cfg = parse_args()
    return run_export(
        cfg=cfg,
        argv=sys.argv,
        platforms_source_path=PLATFORMS_SOURCE_PATH,
        build_output_dir_fn=_build_output_dir,
        build_runtime_dir_fn=_build_runtime_dir,
        build_debug_log_path_fn=_build_debug_log_path,
        scope_mode_fn=_scope_mode,
        diagnostic_summary_fn=_diagnostic_summary,
        manifest_degraded_mode_fn=_manifest_degraded_mode,
        schema_only_fn=_schema_only,
        fixture_mode_fn=_fixture_mode,
        live_mode_fn=_live_mode,
        enforce_mandatory_raw_rows_fn=_enforce_mandatory_raw_rows,
        load_raw_stage_inputs_fn=_load_raw_stage_inputs,
        load_aggregate_stage_input_fn=_load_aggregate_stage_input,
        add_aggregate_contract_diagnostics_fn=_add_aggregate_contract_diagnostics,
        add_slide_source_link_diagnostics_fn=_add_slide_source_link_diagnostics,
        write_tsv_fn=write_tsv,
        write_json_fn=write_json,
        write_jsonl_fn=write_jsonl,
    )


if __name__ == "__main__":
    raise SystemExit(main())
