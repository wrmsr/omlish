import math
import typing as ta

from omlish import check
from omlish import dataclasses as dc


T = ta.TypeVar('T')


class Dims(tuple):
    @classmethod
    def of(cls: ta.Type[T], *dims) -> T:
        return cls(dims)  # type: ignore


class Shape(Dims):
    @property
    def dim(self) -> int:
        return math.prod(self)


class Stride(Dims):
    def offset(self, *idxs: int) -> int:
        check.arg(len(self) == len(idxs))
        return sum(d * i for d, i in zip(self, idxs))


@dc.dataclass(frozen=True)
class ShapeStride:
    shape: int
    stride: int

    @classmethod
    def calc(cls, sh: Shape, st: Stride) -> ta.Sequence['ShapeStride']:
        check.arg(len(sh) == len(st))
        if not sh:
            return []
        ret = [ShapeStride(sh[0], st[0])]
        for i in range(1, len(sh)):
            if (
                    (st[i] != 0 and ret[-1].stride == sh[i] * st[i])
                    or ret[-1].shape == 1 or (st[i] == 0 and ret[-1].stride == 0)
            ):
                ret[-1] = ShapeStride(ret[-1].shape * sh[i], st[i])
            else:
                ret.append(ShapeStride(sh[i], st[i]))
        return ret


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
    print(ShapeStride.calc(sh, st))
    print(ShapeStride.calc(Shape((3, 3)), Stride((3, 1))))
    print(Shape.of(1, 2, 3))
