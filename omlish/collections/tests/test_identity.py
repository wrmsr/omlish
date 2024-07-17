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
