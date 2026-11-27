from __future__ import annotations

from hashlib import sha256
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
PROJECT_ROOT = REPOSITORY_ROOT / "src/comitato/comitato_azure_retirements_v2"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "exports"
COMPONENT_TMP_ROOT = REPOSITORY_ROOT / "tmp/comitato/comitato_azure_retirements_v2"
ACQUISITION_CACHE_ROOT = COMPONENT_TMP_ROOT / "acquisition-cache"


def artifact_destination(logical_path: str) -> str:
    return "support" if logical_path.endswith((".json", ".jsonl")) else "exports"


def _output_namespace(output_root: Path) -> str:
    resolved = output_root.resolve()
    if resolved == DEFAULT_OUTPUT_ROOT.resolve():
        return "default"
    digest = sha256(str(resolved).encode("utf-8")).hexdigest()[:16]
    return f"output-{digest}"


def publication_support_root(output_root: Path) -> Path:
    return COMPONENT_TMP_ROOT / "publications" / _output_namespace(output_root)


def acquisition_cache_root(output_root: Path) -> Path:
    return ACQUISITION_CACHE_ROOT / _output_namespace(output_root)


def resolve_replay_support_bundle(output_root: Path, replay_bundle: Path) -> Path:
    if (replay_bundle / "publication-manifest.json").is_file():
        return replay_bundle
    source_output = replay_bundle.resolve().parent.parent
    for candidate_output in (output_root, DEFAULT_OUTPUT_ROOT, source_output):
        try:
            relative = replay_bundle.resolve().relative_to(candidate_output.resolve())
        except ValueError:
            continue
        return publication_support_root(candidate_output) / relative
    return replay_bundle


__all__ = [
    "ACQUISITION_CACHE_ROOT",
    "COMPONENT_TMP_ROOT",
    "DEFAULT_OUTPUT_ROOT",
    "PROJECT_ROOT",
    "REPOSITORY_ROOT",
    "acquisition_cache_root",
    "artifact_destination",
    "publication_support_root",
    "resolve_replay_support_bundle",
]
