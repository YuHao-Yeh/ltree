# ltree/common/format.py


def format_size_classic(size_bytes: float, human: bool = False) -> str:
    if not human:
        return f"{size_bytes:>8} B"

    for unit in ["B", "K", "M", "G", "T"]:
        if size_bytes < 1024:
            return f"{size_bytes:>5.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:>5.1f} P"
