import pytest

from ..unmodifiable import UnmodifiableMapping
from ..unmodifiable import UnmodifiableSequence
from ..unmodifiable import UnmodifiableSet


def test_unmodifiable():
    l = UnmodifiableSequence([1, 2, 3])
    s = UnmodifiableSet({1, 2, 3})
    d = UnmodifiableMapping({1: 2, 3: 4})

    assert l == [1, 2, 3]
    assert s == {1, 2, 3}
    assert d == {1: 2, 3: 4}

    with pytest.raises(TypeError):
        l[0] = 1  # type: ignore
    with pytest.raises(AttributeError):
        s.add(4)  # type: ignore
    with pytest.raises(TypeError):
        d[5] = 6  # type: ignore
