import pytest

from .. import treapmap as tm
from ..utils import key_cmp


def test_treapmap():
    m: tm.TreapMap[int, str] = tm.TreapMap(_n=None, _c=key_cmp(lambda l, r: l - r))

    for i in range(32):
        m = m.with_(i, str(i))

    m = m.with_(52, "hello")
    m = m.with_(53, "world")
    m = m.with_(52, "Hello")
    m = m.with_(54, "I'm")
    m = m.with_(55, "here")

    print(m)

    it = m.iterate()
    while it.has_next():
        print(it.next())

    print(len(m))

    old = m.with_(500, 'five hundred')
    m = m.without(53)

    with pytest.raises(KeyError):
        print(m[53])
    print(old[53])
    print(old[52])
    print(old[500])

    it = m.iterate()
    while it.has_next():
        print(it.next())
