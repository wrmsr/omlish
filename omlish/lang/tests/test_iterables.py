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
