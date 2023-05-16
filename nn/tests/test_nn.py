import functools
import typing as ta

from omlish import check
from omlish import lang
import numpy as np


if ta.TYPE_CHECKING:
    import torch
else:
    torch = lang.proxy_import('torch')

from ..tensor import Tensor


##


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
    xt = Tensor.of(np.asarray([1., 2.], dtype=np.float32), requires_grad=True)
    yt = Tensor.of(np.asarray([3., 4.], dtype=np.float32), requires_grad=True)

    zt = (xt * yt).sum()
    zt.backward()

    print(xt.get_grad().numpy())
    print(yt.get_grad().numpy())


def torch_test(vs: ta.Sequence[np.ndarray], fn: ta.Callable) -> None:
    def to_np(t: ta.Union[Tensor, torch.Tensor]) -> np.ndarray:
        if isinstance(t, Tensor):
            return t.numpy()
        if isinstance(t, torch.Tensor):
            return t.detach().numpy()
        raise TypeError(t)

    def cmp_ts(our_t: Tensor, tor_t: torch.Tensor) -> None:
        print(to_np(check.isinstance(our_t, Tensor)))
        print(to_np(check.isinstance(tor_t, torch.Tensor)))
        print()

    print()

    our_ts = [Tensor.of(v, requires_grad=True) for v in vs]
    tor_ts = [torch.tensor(v, requires_grad=True) for v in vs]

    our_res = check.isinstance(fn(*our_ts), Tensor)
    tor_res = check.isinstance(fn(*tor_ts), torch.Tensor)
    cmp_ts(our_res, tor_res)

    our_g = (our_res + 1).square().mean()
    tor_g = (tor_res + 1).square().mean()  # noqa
    cmp_ts(our_g, tor_g)

    our_g.backward()
    tor_g.backward()

    for t in our_ts:
        t.get_grad().realize()

    for i, (our_t, tor_t) in enumerate(zip(our_ts, tor_ts)):
        our_tg = our_t.get_grad()
        tor_tg = check.not_none(tor_t.grad)
        cmp_ts(our_tg, tor_tg)


def test_mul_2():
    torch_test([
        np.asarray([1., 2.], dtype=np.float32),
        np.asarray([3., 4.], dtype=np.float32),
    ], lambda l, r: l * r)


##

from ..optimizers import Sgd


np.random.seed(1337)

x_init = np.random.randn(1, 4).astype(np.float32)
w_init = np.random.randn(4, 4).astype(np.float32)
m_init = np.random.randn(1, 4).astype(np.float32)


class TinyNet:

    def __init__(self, tensor: ta.Callable) -> None:
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
                Tensor.of,
                functools.partial(our_optim, config=our_optim.Config(**opts)),
                steps,
            ),
            step(
                torch.tensor,
                tor_optim,
                steps,
                kwargs=opts,
            ),
    ):
        np.testing.assert_allclose(x, y, atol=atol, rtol=rtol)


def _test_sgd(steps, opts, atol, rtol):
    _test_optim(Sgd, torch.optim.SGD, steps, opts, atol, rtol)


def test_sgd():
    _test_sgd(1, {'lr': 0.001}, 1e-6, 0)
