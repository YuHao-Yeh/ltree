# ltree/cli/main.py
import logging
import sys

from ltree.app.logging import configure_logging
from ltree.cli.parser import build_parser


logger = logging.getLogger(__name__)


def main() -> int:
    configure_logging()
    subcommands = {"tree", "theme", "config"}

    argv = getattr(sys, "argv", [])
    if len(argv) < 2:
        if len(argv) == 0:
            argv.append("ltree")
        argv.insert(1, "tree")
    else:
        first_arg = argv[1]
        if first_arg not in subcommands and first_arg not in {
            "-h",
            "--help",
            "-v",
            "--version",
        }:
            argv.insert(1, "tree")

    parser = build_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        try:
            args.func(args)
            return 0
        except PermissionError as e:
            logger.error("Permission denied: %s", e)
            return 1
        except Exception as e:
            logger.error("Unexpected failure: %s", e)
            return 1
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
