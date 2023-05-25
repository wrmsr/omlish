"""
TODO:
 - dataclasses, serde -> datasets/*.yaml
"""
import typing as ta

from omlish import check
from omlish import dataclasses as dc


class DataFile(dc.Data):
    name: str = dc.field(coerce=check.non_empty_str)
    url: str
    md5: ta.Optional[str] = dc.field(kw_only=True)


class DataSet(dc.Data):
    files: ta.Sequence[DataFile]


MNIST = DataSet(
    files=[
        DataFile(
            't10k-images-idx3-ubyte.gz',
            'https://github.com/geohot/tinygrad/tree/a968c4c3a4fbd5ca0171c6fe0f9e86c6b0143bf3/datasets/mnist/t10k-images-idx3-ubyte.gz',  # noqa
            md5='9fb629c4189551a2d022fa330f9573f3',
        ),
        DataFile(
            't10k-labels-idx1-ubyte.gz',
            'https://github.com/geohot/tinygrad/tree/a968c4c3a4fbd5ca0171c6fe0f9e86c6b0143bf3/datasets/mnist/t10k-labels-idx1-ubyte.gz',  # noqa
            md5='ec29112dd5afa0611ce80d1b7f02629c',
        ),
        DataFile(
            'train-images-idx3-ubyte.gz',
            'https://github.com/geohot/tinygrad/tree/a968c4c3a4fbd5ca0171c6fe0f9e86c6b0143bf3/datasets/mnist/train-images-idx3-ubyte.gz',  # noqa
            md5='f68b3c2dcbeaaa9fbdd348bbdeb94873',
        ),
        DataFile(
            'train-labels-idx1-ubyte.gz',
            'https://github.com/geohot/tinygrad/tree/a968c4c3a4fbd5ca0171c6fe0f9e86c6b0143bf3/datasets/mnist/train-labels-idx1-ubyte.gz',  # noqa
            md5='d53e105ee54ea40749a09fcbcd1e9432',
        ),
    ]
)


def test_fetch_mnist():
    print(MNIST)
