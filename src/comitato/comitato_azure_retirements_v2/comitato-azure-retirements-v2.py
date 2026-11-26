import sys
from pathlib import Path


def main() -> None:
    script_path = Path(__file__).resolve()
    if sys.path and Path(sys.path[0] or Path.cwd()).resolve() == script_path.parent:
        sys.path.pop(0)
    repository_root = str(script_path.parents[3])
    if repository_root not in sys.path:
        sys.path.insert(0, repository_root)

    if sys.argv[1:] in (["--help"], ["-h"]):
        from src.comitato.comitato_azure_retirements_v2.src.config import (
            build_parser,
        )

        build_parser().parse_args()

    from src.comitato.comitato_azure_retirements_v2.src.cli import (
        main as run,
    )

    raise SystemExit(run())


if __name__ == "__main__":
    main()
