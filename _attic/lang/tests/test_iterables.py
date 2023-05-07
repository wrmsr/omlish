from .. import iterables as iterables_


def test_peek():
    it = range(4)
    v, it = iterables_.peek(it)
    assert v == 0
    assert list(it) == [0, 1, 2, 3]


def test_multirange():
    assert list(iterables_.multirange(3, (0, 2))) == [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
        (2, 0),
        (2, 1),
    ]
