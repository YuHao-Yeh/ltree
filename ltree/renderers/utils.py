# ltree/renderers/utils.py
from __future__ import annotations

from typing import TYPE_CHECKING
from rich.console import Console
from rich.filesize import decimal as format_size_rich

from ltree.core.utils import format_size_classic

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig
    from ltree.serializers.types import SerializedNode


def print_stats(node: SerializedNode, config: TreeConfig, fmt: str = "text") -> None:
    s = node["stats"]
    size_str = ""
    if config.show_size:
        size = node["metadata"].get("fs")["size"]
        if fmt == "rich":
            size_str = f" ({format_size_rich(size)})"
        else:
            size_str = f" ({format_size_classic(size, config.human_readable).strip()})"

    if fmt == "rich":
        console = Console()
        console.print(f"\n[bold blue]Summary[/]{size_str}:", style="none")
        console.print(
            f"  Visible: [bold cyan]{s["visible_dirs"]:>3}[/] directories, "
            f"[bold cyan]{s["visible_files"]:>3}[/] files"
        )
        console.print(
            f"  Total  : [bold magenta]{s["total_dirs"]:>3}[/] directories, "
            f"[bold magenta]{s["total_files"]:>3}[/] files"
        )
    else:
        print(f"\nSummary{size_str}:")
        print(
            f"Visible: {s["visible_dirs"]:>3} directories, {s["visible_files"]:>3} files"
        )
        print(f"Total  : {s["total_dirs"]:>3} directories, {s["total_files"]:>3} files")
