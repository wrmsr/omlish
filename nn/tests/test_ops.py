import time
import typing as ta

from omlish import check
import numpy as np
import torch

from ..tensor import Tensor


def _test_op(
        shps,
        torch_fxn,
        tinygrad_fxn=None,
        *,
        atol=1e-6,
        rtol=1e-3,
        grad_atol=1e-4,
        grad_rtol=1e-3,
        forward_only=False,
        vals=None,
        a=-0.5,
        b=3,
):
    if tinygrad_fxn is None:
        tinygrad_fxn = torch_fxn
    torch.manual_seed(0)
    np.random.seed(0)
    if shps is None:
        ts = [torch.tensor(x, requires_grad=True) for x in vals]
    else:
        ts = [
            torch.tensor(
                (np.random.random(size=x) + a) * b,
                requires_grad=True,
                dtype=torch.float32,
                )
            for x in shps
        ]

    tst = [Tensor.of(x.detach().numpy(), requires_grad=not forward_only) for x in ts]

    st = time.monotonic()
    out = torch_fxn(*ts)
    torch_fp = time.monotonic() - st

    st = time.monotonic()
    ret = tinygrad_fxn(*tst).realize()
    tinygrad_fp = time.monotonic() - st

    def compare(s, x, y, atol, rtol):
        check.arg(x.shape == y.shape)
        try:
            np.testing.assert_allclose(x, y, atol=atol, rtol=rtol)
        except Exception:
            raise Exception(f'{s} failed shape {x.shape}')

    # if DEBUG >= 6:
    #     np.set_printoptions(linewidth=200, suppress=True)
    #     print(ret.numpy())
    #     print(out.detach().numpy())

    compare('forward pass', ret.numpy(), out.detach().numpy(), atol=atol, rtol=rtol)

    torch_fbp, tinygrad_fbp = np.nan, np.nan
    if not forward_only:
        st = time.monotonic()
        (out + 1).square().mean().backward()
        torch_fbp = time.monotonic() - st

        st = time.monotonic()
        (ret + 1).square().mean().backward()
        for tt in tst:
            tt.get_grad().realize()
        tinygrad_fbp = time.monotonic() - st

        for i, (t, tt) in enumerate(zip(ts, tst)):
            compare(
                f'backward pass tensor {i}',
                tt.get_grad().numpy(),
                t.grad.detach().numpy(),
                atol=grad_atol,
                rtol=grad_rtol,
            )

    print(
        '\ntesting %40r   torch/tinygrad fp: %.2f / %.2f ms  bp: %.2f / %.2f ms '
        % (
            shps,
            torch_fp * 1000,
            tinygrad_fp * 1000,
            torch_fbp * 1000,
            tinygrad_fbp * 1000,
        ),
        end='',
    )


def test_full_like():
    a = Tensor.of([[1, 2, 3], [4, 5, 6]])
    b = torch.tensor([[1, 2, 3], [4, 5, 6]])
    _test_op(
        [],
        lambda: torch.full_like(b, 4),
        lambda: Tensor.full_like(a, 4),
        forward_only=True,
    )


def test_add():
    _test_op([(45, 68), (45, 68)], lambda x, y: x + y, Tensor.add)
