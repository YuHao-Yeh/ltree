# tests/test_core/test_models.py
from ltree.core.models import Stats


# ======================================================================= #
# Tests: Stats Models & Operators
# ======================================================================= #


def test_stats_empty_factory():
    stats = Stats.empty()

    assert stats.visible_dirs == 0
    assert stats.visible_files == 0
    assert stats.hidden_dirs == 0
    assert stats.hidden_files == 0
    assert stats.hidden_size == 0
    assert stats.total_dirs == 0
    assert stats.total_files == 0


def test_stats_reset_visible():
    stats = Stats(
        visible_dirs=3, visible_files=5, hidden_dirs=2, hidden_files=4, hidden_size=100
    )

    stats.reset_visible()

    assert stats.visible_dirs == 0
    assert stats.visible_files == 0
    assert stats.hidden_dirs == 2
    assert stats.hidden_files == 4
    assert stats.hidden_size == 100


def test_stats_addition_operator():
    s1 = Stats(
        visible_dirs=1, visible_files=2, hidden_dirs=3, hidden_files=4, hidden_size=50
    )
    s2 = Stats(
        visible_dirs=10,
        visible_files=20,
        hidden_dirs=30,
        hidden_files=40,
        hidden_size=500,
    )

    res = s1 + s2

    assert res.visible_dirs == 11
    assert res.visible_files == 22
    assert res.hidden_dirs == 33
    assert res.hidden_files == 44
    assert res.hidden_size == 550

    assert s1.visible_dirs == 1
    assert s2.visible_dirs == 10


def test_stats_inplace_addition_operator():
    s1 = Stats(
        visible_dirs=1, visible_files=2, hidden_dirs=3, hidden_files=4, hidden_size=50
    )
    s2 = Stats(
        visible_dirs=10,
        visible_files=20,
        hidden_dirs=30,
        hidden_files=40,
        hidden_size=500,
    )

    s1 += s2

    assert s1.visible_dirs == 11
    assert s1.visible_files == 22
    assert s1.hidden_dirs == 33
    assert s1.hidden_files == 44
    assert s1.hidden_size == 550


def test_stats_subtraction_operator():
    s1 = Stats(
        visible_dirs=15,
        visible_files=25,
        hidden_dirs=35,
        hidden_files=45,
        hidden_size=550,
    )
    s2 = Stats(
        visible_dirs=5, visible_files=5, hidden_dirs=5, hidden_files=5, hidden_size=50
    )

    res = s1 - s2

    assert res.visible_dirs == 10
    assert res.visible_files == 20
    assert res.hidden_dirs == 30
    assert res.hidden_files == 40
    assert res.hidden_size == 500

    assert s1.visible_dirs == 15
    assert s2.visible_dirs == 5


def test_stats_inplace_subtraction_operator():
    s1 = Stats(
        visible_dirs=15,
        visible_files=25,
        hidden_dirs=35,
        hidden_files=45,
        hidden_size=550,
    )
    s2 = Stats(
        visible_dirs=5, visible_files=5, hidden_dirs=5, hidden_files=5, hidden_size=50
    )

    s1 -= s2

    assert s1.visible_dirs == 10
    assert s1.visible_files == 20
    assert s1.hidden_dirs == 30
    assert s1.hidden_files == 40
    assert s1.hidden_size == 500
