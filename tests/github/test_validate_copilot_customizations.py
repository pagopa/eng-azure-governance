from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPOSITORY_ROOT / ".github/scripts/validate-copilot-customizations.sh"


def _write_minimal_repository(
    root: Path,
    *,
    skill_name: str,
    inventory_entries: list[str],
    agents_entries: list[str] | None = None,
) -> Path:
    github_dir = root / ".github"
    scripts_dir = github_dir / "scripts"
    skill_dir = github_dir / "skills" / skill_name
    scripts_dir.mkdir(parents=True)
    skill_dir.mkdir(parents=True)

    validator = scripts_dir / VALIDATOR.name
    shutil.copy2(VALIDATOR, validator)

    (root / "AGENTS.md").write_text(
        "# Repository policy\n\n" + "\n".join(agents_entries or []) + "\n",
        encoding="utf-8",
    )
    (github_dir / "INVENTORY.md").write_text(
        "# Copilot Inventory\n\n"
        + "\n".join(f"- `{entry}`" for entry in inventory_entries)
        + "\n",
        encoding="utf-8",
    )
    (github_dir / "PULL_REQUEST_TEMPLATE.md").write_text(
        "# Pull request\n",
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        f"name: {skill_name}\n"
        "description: Use for a focused repository task.\n"
        "---\n\n"
        f"# {skill_name}\n\n"
        "## When to use\n\n"
        "- Use for the focused task.\n\n"
        "## Validation\n\n"
        "- Run the focused check.\n",
        encoding="utf-8",
    )
    return validator


def _run_validator(validator: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(validator), "--scope", "root", "--mode", "strict"],
        check=False,
        capture_output=True,
        text=True,
    )


def test_strict_validation_accepts_inventory_registered_local_skill(
    tmp_path: Path,
) -> None:
    skill_path = ".github/skills/local-example/SKILL.md"
    validator = _write_minimal_repository(
        tmp_path,
        skill_name="local-example",
        inventory_entries=[skill_path],
    )

    result = _run_validator(validator)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Repository-internal skill" not in result.stdout + result.stderr
    assert "missing skill inventory entry" not in result.stdout + result.stderr


def test_strict_validation_uses_canonical_inventory_not_agents(
    tmp_path: Path,
) -> None:
    skill_path = ".github/skills/internal-example/SKILL.md"
    validator = _write_minimal_repository(
        tmp_path,
        skill_name="internal-example",
        inventory_entries=[],
        agents_entries=[skill_path],
    )

    result = _run_validator(validator)

    assert result.returncode == 1
    assert (
        f"INVENTORY.md is missing skill inventory entry for '{skill_path}'"
        in result.stdout + result.stderr
    )
