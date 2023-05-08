import math

from omlish import check
from omlish import dataclasses as dc


class Shape(tuple):
    @property
    def dim(self) -> int:
        return math.prod(self)


class Stride(tuple):
    def offset(self, *idxs: int) -> int:
        check.arg(len(self) == len(idxs))
        return sum(d * i for d, i in zip(self, idxs))


@dc.dataclass(frozen=True)
class ShapeStride:
    shape: Shape
    stride: Stride


@dc.dataclass(frozen=True)
class View:
    shape: Shape
    stride: Stride
    offset: int = 0


def test_nn():
    sh = Shape((1, 2, 3))
    st = Stride((3, 3, 3))
    v = View(sh, st)
    print(v)
