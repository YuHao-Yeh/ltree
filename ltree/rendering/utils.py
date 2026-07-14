# ltree/rendering/utils.py
from __future__ import annotations

from typing import TYPE_CHECKING
from rich.console import Console
from rich.filesize import decimal as format_size_rich

from ltree.common.format import format_size_classic

if TYPE_CHECKING:
    from ltree.config.config import TreeConfig
    from ltree.tree.models import TreeNode


def print_stats(node: TreeNode, config: TreeConfig, fmt: str = "text") -> None:
    stats = node.stats
    size_str = ""
    if config.show_size:
        size = node.size
        if fmt == "rich":
            size_str = f" ({format_size_rich(size)})"
        else:
            size_str = f" ({format_size_classic(size, config.human_readable).strip()})"

    if fmt == "rich":
        console = Console()
        console.print(f"\n[bold blue]Summary[/]{size_str}:", style="none")
        console.print(
            f"  Visible: [bold cyan]{stats.visible_dirs:>3}[/] directories, "
            f"[bold cyan]{stats.visible_files:>3}[/] files"
        )
        console.print(
            f"  Total  : [bold magenta]{stats.total_dirs:>3}[/] directories, "
            f"[bold magenta]{stats.total_files:>3}[/] files"
        )
    else:
        print(f"\nSummary{size_str}:")
        print(
            f"Visible: {stats.visible_dirs:>3} directories, {stats.visible_files:>3} files"
        )
        print(
            f"Total  : {stats.total_dirs:>3} directories, {stats.total_files:>3} files"
        )
