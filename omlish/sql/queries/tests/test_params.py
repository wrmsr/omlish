import pytest

from ..base import NodeComparisonTypeError
from ..params import Param


def test_params_eq():
    p_anon_0 = Param()
    p_anon_1 = Param()

    p2_0 = Param('p2')
    p2_1 = Param('p2')

    p3 = Param('p3')

    with pytest.raises(NodeComparisonTypeError):
        p_anon_0 == p_anon_1  # noqa

    assert p_anon_0.eq(p_anon_0)
    assert not p_anon_0.eq(p_anon_1)

    assert p2_0.eq(p2_0)
    assert p2_0.eq(p2_1)
    assert p2_1.eq(p2_0)

    assert not p3.eq(p2_0)
    assert not p2_0.eq(p3)
    assert not p3.eq(p_anon_0)

    assert not p2_0.eq(p_anon_0)
    assert not p2_0.eq(p3)
