# ltree/cli/commands/config.py
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ltree.config.config import TreeConfig

if TYPE_CHECKING:
    from argparse import Namespace


def run_config_show(args: Namespace) -> None:
    config = TreeConfig()
    config.load_config_file(args.start_path)

    print("Active Configuration")
    print("=" * 60)

    # for key, value in sorted(asdict(config).items()):
    for key, value in sorted(vars(config).items()):
        if key.startswith("_"):
            continue

        print(f"{key:<25} {value}")


def run_config_locate(args: Namespace) -> None:
    current = Path(args.start_path).resolve()
    found = []

    while True:
        rc = current / ".ltreerc"
        pyproject = current / "pyproject.toml"

        if rc.exists():
            found.append(rc)

        if pyproject.exists():
            found.append(pyproject)

        if current.parent == current:
            break

        current = current.parent

    if not found:
        print("No configuration files found.")
        return

    print("Configuration files:")

    for path in found:
        print(f"  • {path}")


def run_config_validate(args: Namespace) -> None:
    current = Path(args.start_path).resolve()
    checked = False

    while True:
        for filename in (".ltreerc", "pyproject.toml"):
            file = current / filename

            if file.exists():
                checked = True

                try:
                    config = TreeConfig()
                    config.load_config_file(current)
                    print(f"✓ {file}")
                except Exception as exc:
                    print(f"✗ {file}")
                    print(f"    {exc}")

        if current.parent == current:
            break

        current = current.parent

    if not checked:
        print("No configuration files found.")
