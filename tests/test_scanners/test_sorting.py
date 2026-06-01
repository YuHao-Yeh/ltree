# tests/test_scanners/test_sorting.py
from unittest.mock import MagicMock

from ltree.core.config import TreeConfig
from ltree.core.scanners.sorting import sort_entries


# =======================================================================#
# Test: sort_entries()
# =======================================================================#
def test_sort_entries_alphabetical_only():
    config = TreeConfig()
    config.dirs_first = False

    entry1 = MagicMock()
    entry1.name = "b.txt"
    entry1.is_dir.return_value = False

    entry2 = MagicMock()
    entry2.name = "A.txt"
    entry2.is_dir.return_value = False

    entry3 = MagicMock()
    entry3.name = "src"
    entry3.is_dir.return_value = True

    entries = [entry1, entry2, entry3]
    sorted_res = sort_entries(entries, config)

    # Order: A.txt -> b.txt -> src
    assert [e.name for e in sorted_res] == ["A.txt", "b.txt", "src"]


def test_sort_entries_dirs_first():
    config = TreeConfig()
    config.dirs_first = True

    entry1 = MagicMock()
    entry1.name = "main.py"
    entry1.is_dir.return_value = False

    entry2 = MagicMock()
    entry2.name = "tests"
    entry2.is_dir.return_value = True

    entry3 = MagicMock()
    entry3.name = "src"
    entry3.is_dir.return_value = True

    entries = [entry1, entry2, entry3]
    sorted_res = sort_entries(entries, config)

    # Order: src -> tests -> main.py
    assert [e.name for e in sorted_res] == ["src", "tests", "main.py"]
