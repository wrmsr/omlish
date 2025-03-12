import pickle
import typing as ta

import pytest

from ..identity import IdentityKeyDict
from ..identity import IdentitySet


class Incomparable:
    def __eq__(self, other):
        raise TypeError


def test_identity_key_dict():
    x, y = Incomparable(), Incomparable()
    with pytest.raises(TypeError):
        {x: 0, y: 1}  # noqa
    dct: ta.MutableMapping[ta.Any, int] = IdentityKeyDict()
    with pytest.raises(KeyError):
        dct[x]  # noqa
    dct[x] = 4
    dct[y] = 5
    assert dct[x] == 4
    assert dct[y] == 5
    dct[x] = 6
    assert dct[x] == 6
    assert dct[y] == 5
    assert list(dct)[0] is x  # noqa
    assert list(dct)[1] is y
    del dct[y]
    with pytest.raises(KeyError):
        dct[y]  # noqa
    assert dct[x] == 6


def test_identity_key_set():
    x, y = Incomparable(), Incomparable()
    with pytest.raises(TypeError):
        {x, y}  # noqa
    st: ta.MutableSet[ta.Any] = IdentitySet()
    assert len(st) == 0
    st.add(x)
    assert len(st) == 1
    assert x in st
    assert y not in st
    st.add(y)
    assert len(st) == 2
    assert x in st
    assert y in st
    st.remove(x)
    assert x not in st
    assert y in st


class PickleA:
    def __hash__(self):
        raise TypeError

    def __eq__(self, other):
        raise TypeError


class PickleC:
    def __init__(self):
        self.a = PickleA()
        self.b = PickleA()

        self.s = IdentitySet([self.a, self.b])
        self.m: ta.Any = IdentityKeyDict([(self.a, 'a'), (self.b, 'b')])


def test_pickle():
    def check_c(c):
        assert c.a in c.s
        assert c.b in c.s
        assert PickleA() not in c.s
        assert c.m[c.a] == 'a'
        assert c.m[c.b] == 'b'
        assert PickleA() not in c.m

    c = PickleC()
    check_c(c)

    s = pickle.dumps(c)
    c2 = pickle.loads(s)  # noqa

    check_c(c2)
    assert c2.a is not c.a
