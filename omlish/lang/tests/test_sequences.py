import itertools

import pytest

from ..sequences import SeqView
from ..sequences import iterrange


##


def assert_matches_slice(seq, start, stop, step):
    expected = seq[slice(start, stop, step)]
    got = list(iterrange(seq, start, stop, step))
    assert got == list(expected), (
        f'Mismatch for seq={seq!r}, start={start}, stop={stop}, step={step}: '
        f'expected {list(expected)!r}, got {got!r}'
    )


def test_iterrange_matches_slice():
    seqs = [
        list(range(5)),
        list(range(10)),
        'abcdef',
        tuple('wxyz'),
    ]
    starts = [None, 0, 1, 2, -1, -3, -10, 10]
    stops = [None, 0, 1, 3, -1, -3, -10, 10]
    steps = [None, 1, 2, 3, -1, -2, -3]

    for seq, start, stop, step in itertools.product(seqs, starts, stops, steps):
        assert_matches_slice(seq, start, stop, step)


def test_iterrange_full_defaults():
    seq = [0, 1, 2, 3, 4]
    assert list(iterrange(seq)) == seq


def test_iterrange_negative_step_defaults():
    seq = [0, 1, 2, 3, 4]
    # start/stop None + negative step should mirror seq[::-1], seq[3::-1], etc.
    assert list(iterrange(seq, None, None, -1)) == seq[::-1]
    assert list(iterrange(seq, 3, None, -1)) == seq[3::-1]
    assert list(iterrange(seq, None, 1, -1)) == seq[:1:-1]  # [] since stop=1 is exclusive


def test_iterrange_bounds_clamped():
    seq = [0, 1, 2]
    assert list(iterrange(seq, -100, 100, 1)) == seq[:]
    assert list(iterrange(seq, 100, -100, -1)) == seq[::-1]


def test_iterrange_zero_step_raises():
    with pytest.raises(ValueError):  # noqa
        list(iterrange([1, 2, 3], 0, 2, 0))


##


def test_seq_view():
    a = list(range(10))

    v = SeqView(a, slice(2, 9, 2))  # indices: [2,4,6,8]
    assert list(v) == [2, 4, 6, 8]
    assert v[1] == 4
    assert len(v) == 4

    w = SeqView(v, slice(1, None, -1))  # v[1::-1] -> [4,2]
    assert list(w) == [4, 2]
    assert w.data is a  # flattened
    assert isinstance(w, SeqView)

    u = v[1:]  # indices: [4,6,8]
    assert isinstance(u, SeqView)
    assert list(u) == [4, 6, 8]

    assert v.count(4) == 1
    assert v.index(6) == 2
    with pytest.raises(ValueError):  # noqa
        v.index(42)

    assert a[v.slice] == list(v) == v.materialize()
