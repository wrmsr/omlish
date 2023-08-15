import numpy as np

from ..tensor import Tensor


def test_simple_bin2red():
    sz = 1024
    np.random.seed(0)
    a = 0.
    b = 1.
    x, y, z = [Tensor(np.random.random(size=(sz, sz)).astype(np.float32) + a) * b for _ in range(3)]
    i = ((x * 0.420) * (y * 0.69)) + (z * 0.123)
    j = i.sum()
    print(j.numpy())


# def test_matmul():
#     sz = 1024
#     np.random.seed(0)
#     a = 0.0
#     b = 1.0
#     x, y = [Tensor(np.random.random(size=(sz, sz)).astype(np.float32) + a) * b for _ in range(2)]
#     i = x @ y
#     j = i.sum()
#     print(j.numpy())
