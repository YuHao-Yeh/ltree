import argparse
import sys

from .core import scan_tree
from .config import TreeConfig
from .exporters import (
    render_text, render_json, render_markdown, render_markdown_as_block,
    print_stats
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ltree: A customizable directory tree viewer.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # --- Basic ---
    basic = parser.add_argument_group('Basic Options')
    basic.add_argument('start_path', nargs='?', default='.', 
                       help='Starting directory path (default: current directory).')
    basic.add_argument('-o', '--output', default='-', 
                       help='Output file name. Use "-" for stdout (default).')

    # --- Output Format ---
    output = parser.add_argument_group('Output Formatting')
    output.add_argument('-F', '--format', dest='format',
                        choices=['text', 'json', 'md', 'markdown', 'block'],
                        default='text', help='Output format (default: text).')
    output.add_argument('-c', '--color', action='store_true', 
                        help='Enable colored output.', dest='color')
    output.add_argument('-s', '--size', action='store_true', 
                        help='Show file size.', dest='show_size') # reserved func
    output.add_argument('-H', '--human', action='store_true', dest='human_readable',
                        help='Show size in human-readable format (e.g., 1K 2M).')   # 新功能預留

    # --- Filter Rules ---
    filtering = parser.add_argument_group('Filtering Rules')
    filtering.add_argument('-a', '--all', action='store_true', dest='show_all',
                           help='Show hidden files and directories.') # 新功能預留
    filtering.add_argument('-d', '--dirs-only', action='store_true', 
                           help='Only display directories.', dest='folders_only')
    filtering.add_argument('--ex-dirs', action='append', default=[], 
                           help='Exclude directories.', metavar='DIR', dest='ex_dirs')
    filtering.add_argument('-I', '--ex-files', action='append', default=[], metavar='PATTERN',
                           help='Exclude files (supports wildcards).', dest='ex_files')
    filtering.add_argument('--ex-ext', action='append', default=[], 
                           help='Exclude by file extension (e.g., .log).', dest='ex_ext')
    filtering.add_argument('--ex-prefix', action='append', default=[],
                           help='Exclude by prefix.', dest='ex_prefix')
    filtering.add_argument('--add-dirs', action='append', default=[],
                           help='Re-include specific directories.', dest='add_dirs')
    filtering.add_argument('--add-files', action='append', default=[], 
                           help='Re-include specific files.', dest='add_files')

    # --- Display Options ---
    display = parser.add_argument_group('Display Options')
    display.add_argument('-L', '--max-depth', type=int, default=None, 
                         help='Limit directory depth.', dest='max_depth')
    display.add_argument('-f', '--full-path', action='store_true', dest='full_path',
                         help='Print the full path prefix for every file.')
    display.add_argument('--dirs-first', action='store_true', 
                         help='List directories before files.', dest='dirs_first')
    display.add_argument('--show-ellipsis', action='store_true', 
                         help='Show "..." when depth is truncated.', dest='show_ellipsis')

    return parser.parse_args()

def run(args: argparse) -> None:
    config = TreeConfig()
    config.apply_args(args)

    is_console = (args.output == '-')
    if is_console:
        output_file = sys.stdout
    else:
        output_file = open(args.output, 'w', encoding='utf-8')
  
    try:
        root = scan_tree(
            path=args.start_path,
            config=config,
            max_depth=args.max_depth
        )

        if not root:
            return
        
        match args.format:
            case "json":
                render_json(node=root, file=output_file, config=config)
            case "markdown" | "md":
                render_markdown(node=root, file=output_file, config=config)
            case "block":
                render_markdown_as_block(node=root, file=output_file, config=config)
            case "text":
                render_text(node=root, file=output_file, config=config)
            case _:
                print("Unsupport format")
                return
        if is_console:
            print_stats(root, config)

    finally:
        if not is_console:
            output_file.close()
            print(f"Directory tree written to {args.output}")

def main():
    run(parse_args())

if __name__ == '__main__':
    main()
