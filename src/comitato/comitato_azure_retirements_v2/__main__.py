import sys


def main() -> None:
    if sys.argv[1:] in (['--help'], ['-h']):
        from .config import _parser

        _parser().parse_args()
    from .cli import main as run

    raise SystemExit(run())


if __name__ == "__main__":
    main()
