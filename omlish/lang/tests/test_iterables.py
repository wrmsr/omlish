from ..iterables import common_prefix_len
from ..iterables import itergen
from ..iterables import peek
from ..iterables import prodrange


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
