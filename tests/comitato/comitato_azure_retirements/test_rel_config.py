from __future__ import annotations

from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements.libs import config


def test_load_rel_config_reads_regions_and_logging_settings(tmp_path: Path) -> None:
    assert hasattr(config, "load_rel_config"), "azure_rel.conf loader is missing"

    config_path = tmp_path / "azure_rel.conf"
    config_path.write_text(
        """
[regions]
allowed =
    italynorth
    westeurope
    global

[logging]
enabled = true
level = WARNING
console_level = ERROR
include_traceback = true
log_directory = logs
""".strip(),
        encoding="utf-8",
    )

    resolved = config.load_rel_config(config_path)

    assert resolved.allowed_regions == frozenset({"italynorth", "westeurope", "global"})
    assert resolved.logging.enabled is True
    assert resolved.logging.level == "WARNING"
    assert resolved.logging.console_level == "ERROR"
    assert resolved.logging.include_traceback is True
    assert resolved.logging.log_directory == tmp_path / "logs"


def test_load_rel_config_rejects_unknown_log_level(tmp_path: Path) -> None:
    assert hasattr(config, "load_rel_config"), "azure_rel.conf loader is missing"

    config_path = tmp_path / "azure_rel.conf"
    config_path.write_text(
        """
[regions]
allowed = italynorth

[logging]
enabled = true
level = EVERYTHING
console_level = INFO
include_traceback = true
log_directory =
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="logging.level"):
        config.load_rel_config(config_path)
