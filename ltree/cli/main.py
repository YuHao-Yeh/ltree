# ltree/cli/main.py
import sys

from ltree.cli.parser import build_parser


def main() -> int:
    subcommands = {"tree", "theme"}

    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        if first_arg not in subcommands and first_arg not in {
            "-h",
            "--help",
            "-v",
            "--version",
        }:
            sys.argv.insert(1, "tree")
    elif len(sys.argv) == 1:
        sys.argv.insert(1, "tree")

    parser = build_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        try:
            args.func(args)
            return 0
        except PermissionError as e:
            print(f"Error: Permission denied. {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error: Unexpected failure. {e}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
