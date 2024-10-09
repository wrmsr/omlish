import typing as ta

from omlish import lang
from omlish.testing import pytest as ptu

from ..similarity import Similarity
from ..similarity import calc_similarities
from ..vectors import Vector


if ta.TYPE_CHECKING:
    import numpy as np
else:
    np = lang.proxy_import('numpy')


@ptu.skip.if_cant_import('numpy')
def test_calc():
    a = np.array([
        [0., .5, 1.],
        [1., .5, 1.],
    ])
    b = np.array([.2, .3, .4])

    assert np.allclose(calc_similarities(Similarity.DOT, a, b), np.array([0.55, 0.75]))
    assert np.allclose(calc_similarities(Similarity.COSINE, a, b), np.array([0.91350028, 0.92847669]))
