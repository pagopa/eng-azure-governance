from pathlib import Path
import re


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GITHUB_DIRECTORY = REPOSITORY_ROOT / ".github"


def test_inventory_matches_installed_customizations() -> None:
    inventory = (GITHUB_DIRECTORY / "INVENTORY.md").read_text(encoding="utf-8")
    entries = re.findall(
        r"`(\.github/(?:instructions|prompts|skills|agents)/[^`]+)`", inventory
    )
    installed = {
        file.relative_to(REPOSITORY_ROOT).as_posix()
        for pattern in (
            "instructions/**/*.instructions.md",
            "prompts/**/*.prompt.md",
            "skills/**/SKILL.md",
            "agents/**/*.agent.md",
        )
        for file in GITHUB_DIRECTORY.glob(pattern)
        if file.is_file()
    }

    assert len(entries) == len(set(entries)), "Duplicate inventory entries"
    assert set(entries) == installed
