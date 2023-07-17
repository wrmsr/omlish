from tinygrad.tensor import Tensor as TgTensor

from nn.tensor import Tensor

from ..ops import convert_from_tg_lazy


def test_ops():
    tgx = TgTensor([1, 2, 3]) + 2
    print(tgx.numpy())

    x = Tensor([1, 2, 3]) + 2
    print(x.numpy())

    print(convert_from_tg_lazy(tgx.lazydata))
