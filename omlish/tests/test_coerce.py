import typing as ta

import pytest

from .. import coerce
from .. import collections as col


def test_coerce():
    r = coerce.seq_of(str)([1, 2])
    assert r == ['1', '2']
    assert isinstance(r, col.Frozen)
    assert isinstance(r, ta.Sequence)

    c = coerce.seq_of((int,))  # type: ignore
    assert c([1, 2]) == [1, 2]
    with pytest.raises(TypeError):
        c([1, '2'])

    c = coerce.seq_of((int, None))  # type: ignore
    assert c([1, 2, None]) == [1, 2, None]
