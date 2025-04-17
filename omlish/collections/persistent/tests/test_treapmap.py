import pytest

from ...utils import key_cmp
from .. import treapmap as tm


def test_treapmap():
    m: tm.TreapMap[int, str] = tm.TreapMap(_n=None, _c=key_cmp(lambda l, r: l - r))

    for i in range(32):
        m = m.with_(i, str(i))

    m = m.with_(52, 'hello')
    m = m.with_(53, 'world')
    m = m.with_(52, 'Hello')
    m = m.with_(54, "I'm")
    m = m.with_(55, 'here')

    print(m)
    print('===')

    it = m.items()
    while it.has_next():
        print(it.next())
    print('===')

    print(len(m))
    print('===')

    old = m.with_(500, 'five hundred')
    m = m.without(53)

    with pytest.raises(KeyError):
        print(m[53])
    print(old[53])
    print(old[52])
    print(old[500])
    print('===')

    it = m.items()
    while it.has_next():
        print(it.next())
    print('===')

    rit = m.items_desc()
    while rit.has_next():
        print(rit.next())
    print('===')

    it = m.items_from(30)
    while it.has_next():
        print(it.next())
    print('===')

    rit = m.items_from_desc(30)
    while rit.has_next():
        print(rit.next())
    print('===')
