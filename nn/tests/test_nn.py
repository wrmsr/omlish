import math
import typing as ta

from omlish import cached
from omlish import check
from omlish import dataclasses as dc


T = ta.TypeVar('T')


class Dims(tuple):
    def __new__(cls, *args, **kwargs):
        if kwargs:
            raise TypeError
        if not args:
            return super().__new__(cls)
        if isinstance(args[0], int):
            t = args
        else:
            [t] = args
            t = tuple(t)
        for d in t:
            if not isinstance(d, int):
                raise TypeError(d)
        return super().__new__(cls, t)


class Shape(Dims):
    @property
    def dim(self) -> int:
        return math.prod(self)

    def base_stride(self) -> 'Stride':
        sts = [0] * len(self)
        sts[-1] = 1
        for i in range(len(self) - 2, -1, -1):
            sts[i] = sts[i + 1] * self[i + 1]
        return Stride(st if s != 1 else 0 for st, s in zip(sts, self))


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

    @staticmethod
    def of(sh: Shape) -> 'View':
        check.arg(len(sh) > 0)
        return View(sh, sh.base_stride())

    @cached.property
    def shape_strides(self) -> ta.Sequence[ShapeStride]:
        return ShapeStride.calc(self.shape, self.stride)


class ShapeTracker:
    pass


def test_nn():
    sh = Shape(1, 2, 3)
    st = Stride(3, 3, 3)
    v = View(sh, st)
    print(v)
    print(v.shape_strides)
    print(v.shape_strides)
    print(View.of(sh))
