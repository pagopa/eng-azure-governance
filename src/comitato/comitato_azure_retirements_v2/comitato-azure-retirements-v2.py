import sys
from pathlib import Path


def main() -> None:
    repository_root = str(Path(__file__).resolve().parents[3])
    if repository_root not in sys.path:
        sys.path.insert(0, repository_root)

    if sys.argv[1:] in (["--help"], ["-h"]):
        from src.comitato.comitato_azure_retirements_v2.retirements.config import (
            build_parser,
        )

        build_parser().parse_args()

    from src.comitato.comitato_azure_retirements_v2.retirements.cli import (
        main as run,
    )

    raise SystemExit(run())


if __name__ == "__main__":
    main()