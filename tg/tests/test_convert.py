from tinygrad.tensor import Tensor as TgTensor

from nn.tensor import Tensor

from ..convert import convert_tg


def test_ops():
    tgx = TgTensor([1, 2, 3]) + 2
    print(tgx.numpy())

    x = Tensor([1, 2, 3]) + 2
    print(x.numpy())

    print(convert_tg(tgx.lazydata))
