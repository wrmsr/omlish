from ..frozen import frozendict


def test_frozendict():
    fd: frozendict[int, int] = frozendict([(1, 2), (3, 4)])
    assert fd[3] == 4
