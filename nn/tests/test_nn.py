import numpy as np

from ..tensor import Tensor


def test_nn():
    print()

    xa = np.asarray([1., 2.], dtype=np.float32)
    ya = np.asarray([3., 4.], dtype=np.float32)
    print(xa)
    print(ya)

    xt = Tensor.of(xa)  # noqa
    yt = Tensor.of(ya)  # noqa

    zt = xt * yt  # noqa

    zt.realize()

    za = zt.numpy()
    print(za)

    # za = zt.realized().to_cpu()
    # print(za)


def test_mul_backward():
    xt = Tensor(np.asarray([1., 2.], dtype=np.float32), requires_grad=True)
    yt = Tensor(np.asarray([3., 4.], dtype=np.float32), requires_grad=True)

    zt = (xt * yt).sum()
    zt.backward()

    print(xt.grad.numpy())
    print(yt.grad.numpy())
