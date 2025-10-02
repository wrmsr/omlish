import itertools

import pytest

from ..iterables import common_prefix_len
from ..iterables import consume
from ..iterables import itergen
from ..iterables import iterrange
from ..iterables import peek
from ..iterables import prodrange


def test_consume():
    l = []

    def f():
        for i in range(3):
            yield i
            l.append(i)

    g = f()
    assert not l
    consume(g)

    with pytest.raises(StopIteration):
        next(g)

    assert l == list(range(3))


def test_peek():
    it = range(4)
    v, it = peek(it)  # type: ignore
    assert v == 0
    assert list(it) == [0, 1, 2, 3]


def test_prodrange():
    assert list(prodrange(3, (0, 2))) == [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
        (2, 0),
        (2, 1),
    ]


def test_itergen():
    l = list(reversed(range(3)))

    a = enumerate(l)
    assert list(a) == [(0, 2), (1, 1), (2, 0)]
    assert list(a) == []

    b = itergen(lambda: enumerate(l))
    for _ in range(2):
        assert list(b) == [(0, 2), (1, 1), (2, 0)]


def test_common_prefix_len():
    assert common_prefix_len() == 0
    assert common_prefix_len('a', 'b') == 0
    assert common_prefix_len('aa', 'ab') == 1
    assert common_prefix_len('ab', 'ab') == 2
    assert common_prefix_len('ab', 'abc', 'ab') == 2
    assert common_prefix_len('ab', 'abc', 'abd') == 2
    assert common_prefix_len('abc', 'abce', 'abcd') == 3
    assert common_prefix_len('aba', 'aca') == 1


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
