import numpy as np

from ..tensor import Tensor


def test_nn():
    # t = Tensor()

    xa = np.asarray([1., 2.], dtype=np.float32)
    ya = np.asarray([3., 4.], dtype=np.float32)

    xt = Tensor.of(xa)  # noqa
    yt = Tensor.of(ya)  # noqa

    zt = xt * yt  # noqa

    # za = zb.realize().realized().to_cpu()
    # print(za)
