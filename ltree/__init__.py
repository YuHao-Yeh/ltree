# ltree/__init__.py
from __future__ import annotations

import re
from pathlib import Path


def _get_version() -> str:
    try:
        import importlib.metadata

        return importlib.metadata.version("ltree-cli")
    except Exception:
        pass

    try:
        current_dir = Path(__file__).resolve().parent
        for parent in [current_dir] + list(current_dir.parents):
            pyproject = parent / "pyproject.toml"
            if pyproject.exists():
                with open(pyproject, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("version"):
                            match = re.search(
                                r'version\s*=\s*["\']([^"\']+)["\']', line
                            )
                            if match:
                                return match.group(1)
    except Exception:
        pass

    return "0.3.0"


__version__ = _get_version()
