"""
https://pytorch.org/tutorials/beginner/basics/data_tutorial.html
"""
import typing as ta

from omlish import lang
from omlish.testing import pytest as ptu


if ta.TYPE_CHECKING:
    import torchvision.datasets as tv_ds
    import torchvision.transforms as tv_tfm

else:
    tv_ds = lang.proxy_import('torchvision.datasets')
    tv_tfm = lang.proxy_import('torchvision.transforms')


@ptu.skip_if_cant_import('torchvision')
def test_torch():
    root = '.cache/torch_data'

    training_data = tv_ds.FashionMNIST(  # noqa
        root=root,
        train=True,
        download=True,
        transform=tv_tfm.ToTensor(),
    )

    test_data = tv_ds.FashionMNIST(  # noqa
        root=root,
        train=False,
        download=True,
        transform=tv_tfm.ToTensor(),
    )
