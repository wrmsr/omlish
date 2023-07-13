import unittest

import numpy as np
import torch

from tinygrad.tensor import Tensor


class TestSimple(unittest.TestCase):
    def test_simple(self):
        xa = np.asarray([1.0, 2.0], dtype=np.float32)
        ya = np.asarray([3.0, 4.0], dtype=np.float32)
        print(xa)
        print(ya)

        xt = Tensor(xa)  # noqa
        yt = Tensor(ya)  # noqa

        zt = xt * yt  # noqa

        zt.realize()

        za = zt.numpy()
        print(za)

    def test_mul_backward(self):
        xt = Tensor(np.asarray([1.0, 2.0], dtype=np.float32), requires_grad=True)
        yt = Tensor(np.asarray([3.0, 4.0], dtype=np.float32), requires_grad=True)

        zt = (xt * yt).sum()
        zt.backward()

        print(zt.numpy())
        print(xt.grad.numpy())
        print(yt.grad.numpy())

    def test_big_sum(self):
        xt = Tensor(np.arange(1_000, dtype=np.float32), requires_grad=True)
        zt = xt.sum()
        print(zt.numpy())

    def test_matmul(self):
        shps = [64, (64, 99)]
        np.random.seed(0)
        a = -0.5
        b = 3
        ts = [
            torch.tensor(
                (np.random.random(size=x) + a) * b,
                requires_grad=True,
                dtype=torch.float32,
            )
            for x in shps
        ]

        tst = [Tensor(x.detach().numpy(), requires_grad=True) for x in ts]
        x, y = tst
        ret: Tensor = x.matmul(y).realize()

        print(ret.numpy())


##


from tinygrad.nn.optim import SGD


np.random.seed(1337)

x_init = np.random.randn(1, 4).astype(np.float32)
w_init = np.random.randn(4, 4).astype(np.float32)
m_init = np.random.randn(1, 4).astype(np.float32)


class TinyNet:

    def __init__(self, tensor) -> None:
        super().__init__()

        self.x = tensor(x_init.copy(), requires_grad=True)
        self.w = tensor(w_init.copy(), requires_grad=True)
        self.m = tensor(m_init.copy())

    def forward(self):
        out = self.x.matmul(self.w).relu()
        out = out.log_softmax(1)
        out = out.mul(self.m).add(self.m).sum()
        return out


def step(tensor, optim, steps=1, **kwargs):
    net = TinyNet(tensor)
    optim = optim([net.x, net.w], **kwargs)
    for _ in range(steps):
        out = net.forward()
        optim.zero_grad()
        out.backward()
        optim.step()
    return net.x.detach().numpy(), net.w.detach().numpy()


def _test_optim(
    our_optim,
    tor_optim,
    steps,
    opts,
    atol,
    rtol
):
    for x, y in zip(
        step(
            Tensor,
            our_optim,
            steps,
            **opts,
        ),
        step(
            torch.tensor,
            tor_optim,
            steps,
            **opts,
        ),
    ):
        np.testing.assert_allclose(x, y, atol=atol, rtol=rtol)


def _test_sgd(steps, opts, atol, rtol):
    _test_optim(SGD, torch.optim.SGD, steps, opts, atol, rtol)


class TestSgd(unittest.TestCase):
    def test_sgd(self):
        _test_sgd(1, {'lr': 0.001}, 1e-6, 0)


##


if __name__ == "__main__":
    np.random.seed(1337)
    unittest.main(verbosity=2)
