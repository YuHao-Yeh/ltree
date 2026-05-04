import argparse
import sys

from .core import list_dir, scan_tree
from .config import TreeConfig
from .schema import Stats
from .exporters import render_text, render_json, render_markdown, print_stats, render_markdown_as_block


def parse_args():
    parser = argparse.ArgumentParser(description="List directory structure as a tree.")
    parser.add_argument('start_path', nargs='?', default='.', help='Starting directory path (default: current directory)')
    parser.add_argument('-o', '--output', default='tree.txt', help='Output file name (default: tree.txt). Use "-" to print to stdout.')
    parser.add_argument('-f', '--format', choices=['text', 'json', 'markdown', 'md', 'md_block'], default='text', help='Output format')
    parser.add_argument('--no-color', action='store_true', help='Disable color output even if printing to console', dest='no_color')
    parser.add_argument('--ex-dirs', '--exclude-dirs', action='append', default=[], help='Exclude certain directory', dest='ex_dirs')
    parser.add_argument('--ex-files', '--exclude-files', action='append', default=[], help='Exclude certain files', dest='ex_files')
    parser.add_argument('--add-dirs', action='append', default=[], help='Add certain directory', dest='add_dirs')
    parser.add_argument('--add-files', action='append', default=[], help='Add certain files', dest='add_files')
    parser.add_argument('--ex-ext', '--exclude-ext', action='append', default=[], help='Exclude files with these extensions (e.g., --exclude-ext .py)', dest='ex_ext')
    parser.add_argument('--ex-prefix', '--exclude-prefix', action='append', default=[], help='Exclude items (files or folders) that start with this prefix', dest='ex_prefix')
    parser.add_argument('-d', '--dirs-only', action='store_true', help='Only display directories, not files', dest='folders_only')
    parser.add_argument('-L', '--max-depth', type=int, default=None, help='Limit directory depth', dest='max_depth')
    parser.add_argument('--dirs-first', action='store_true', help='List directories before files', dest='dirs_first')
    parser.add_argument('--show-ellipsis', action='store_true', help='Show "..." when depth is truncated', dest='show_ellipsis')

    args = parser.parse_args()

    return args

def run(args: argparse):
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
            max_depth=args.max_depth,
            folders_only=args.folders_only
        )

        match args.format:
            case "json":
                render_json(node=root, file=output_file)
            case "markdown" | "md":
                render_markdown(node=root, file=output_file)
            case "md_block":
                render_markdown_as_block(node=root, file=output_file, config=config)
            case "text":
                render_text(node=root, file=output_file, config=config)
            case _:
                print("Unsupport format")
                return
        if is_console:
            print_stats(root)

        """
        stats = Stats()

        list_dir(
            start_path=args.start_path, 
            file=output_file, 
            is_console=is_console, 
            stats=stats, 
            use_color=(not args.no_color),
            folders_only=args.folders_only,
            dirs_first=args.dirs_first,
            show_ellipsis=args.show_ellipsis,
            max_depth=args.max_depth,
            config=config,
            is_root=True
        )
        if is_console:
            total_dirs = stats.visible_dirs + stats.hidden_dirs
            total_files = stats.visible_files + stats.hidden_files

            print(f"\nVisible: {stats.visible_dirs:>3} dir(s), {stats.visible_files:>3} file(s)")
            print(f"Total  : {total_dirs:>3} dir(s), {total_files:>3} file(s)")
        """
    finally:
        if not is_console:
            output_file.close()
            print(f"Directory tree written to {args.output}")

def main():
    run(parse_args())

if __name__ == '__main__':
    main()
