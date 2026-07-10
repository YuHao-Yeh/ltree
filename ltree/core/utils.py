# ltree/core/utils.py
from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from io import TextIOWrapper
    from os import PathLike
    from typing import TextIO


def relative_path(target_path: str | PathLike[str], base_path: str | PathLike[str]):
    abs_target = os.path.abspath(target_path)
    abs_base = os.path.abspath(base_path)

    if abs_target == abs_base:
        return "."

    rel = os.path.relpath(abs_target, abs_base)

    return rel.replace("\\", "/")


def write_line(file: TextIO | TextIOWrapper | None = None, text: str = "") -> None:
    if file is None:
        return
    file.write(text + "\n")


def format_size_classic(size_bytes: float, human: bool = False) -> str:
    if not human:
        return f"{size_bytes:>8} B"

    for unit in ["B", "K", "M", "G", "T"]:
        if size_bytes < 1024:
            return f"{size_bytes:>5.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:>5.1f} P"
