"""
https://pytorch.org/tutorials/beginner/basics/data_tutorial.html
"""
import typing as ta

from omdev.cache import data as daca
from omlish import lang
from omlish.testing import pytest as ptu


if ta.TYPE_CHECKING:
    import torchvision as tv  # noqa
    import torchvision.datasets  # noqa
    import torchvision.transforms  # noqa

else:
    tv = lang.proxy_import('torchvision', extras=['datasets', 'transforms'])  # noqa


FASHION_MNIST_SPECS = {
    file: daca.UrlSpec(
        f'https://ossci-datasets.s3.amazonaws.com/mnist/{file}',
    )
    for file, md5 in [  # noqa
        ('train-images-idx3-ubyte.gz', 'f68b3c2dcbeaaa9fbdd348bbdeb94873'),
        ('train-labels-idx1-ubyte.gz', 'd53e105ee54ea40749a09fcbcd1e9432'),
        ('t10k-images-idx3-ubyte.gz', '9fb629c4189551a2d022fa330f9573f3'),
        ('t10k-labels-idx1-ubyte.gz', 'ec29112dd5afa0611ce80d1b7f02629c'),
    ]
}


@ptu.skip.if_cant_import('torchvision')
def test_torch():
    for spec in FASHION_MNIST_SPECS.values():
        print(daca.default().get(spec))

    # root = '.cache/torch_data'

    # training_data = tv.datasets.FashionMNIST(  # noqa
    #     root=root,
    #     train=True,
    #     download=True,
    #     transform=tv.transforms.ToTensor(),
    # )

    # test_data = tv.transforms.FashionMNIST(  # noqa
    #     root=root,
    #     train=False,
    #     download=True,
    #     transform=tv.transforms.ToTensor(),
    # )
