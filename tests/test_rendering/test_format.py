# tests/test_rendering/test_format.py
from ltree.common.format import format_size_classic


# ======================================================================= #
# Tests: format_size_classic
# ======================================================================= #
def test_format_size_classic():
    # Raw Bytes
    assert format_size_classic(100, human=False) == "     100 B"
    assert format_size_classic(1024, human=False) == "    1024 B"

    # Human Readable
    assert format_size_classic(500, human=True) == "500.0 B"
    assert format_size_classic(1024, human=True) == "  1.0 K"
    assert format_size_classic(1024**2 * 1.5, human=True) == "  1.5 M"
    assert format_size_classic(1024**5 * 1.5, human=True) == "  1.5 P"
