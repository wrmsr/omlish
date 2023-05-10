import math
import typing as ta

from omlish import cached
from omlish import check
from omlish import dataclasses as dc

from .dims import Shape
from .dims import ShapeStride
from .dims import Stride


@dc.dataclass(frozen=True)
class View:
    shape: Shape
    stride: Stride
    offset: int = 0
    mask: ta.Any = None  # FIXME: ta.Optional[ta.Tuple[ta.Tuple[int, int], ...]]

    @staticmethod
    def of_shape(sh: Shape) -> 'View':
        check.arg(len(sh) > 0)
        return View(sh, sh.base_stride())

    @cached.property
    def shape_strides(self) -> ta.Sequence[ShapeStride]:
        return ShapeStride.calc(self.shape, self.stride)


class ShapeTracker:
    def __init__(
            self,
            shape: ta.Union[Shape, 'ShapeTracker'],
            views: ta.Optional[ta.Iterable['View']] = None,
    ) -> None:
        super().__init__()

        if views is not None:
            self._views = list(views)
        elif isinstance(shape, ShapeTracker):
            self._views = list(shape._views)
        else:
            self._views = [View.of_shape(shape)]

    @staticmethod
    def of(o: ta.Union['ShapeTracker', Shape]) -> 'ShapeTracker':
        if isinstance(o, ShapeTracker):
            return o
        if isinstance(o, Shape):
            return ShapeTracker(o)
        raise TypeError(o)

    @property
    def view(self) -> View:
        return self._views[-1]

    @property
    def shape(self) -> Shape:
        return self.view.shape

    @property
    def size(self) -> int:
        v = self.view
        return math.prod([s for s, st in zip(v.shape, v.stride) if st != 0])

    def movement_op(self, op, arg: ta.Union[ta.Tuple[int, ...], ta.Tuple[ta.Tuple[int, int], ...]]) -> 'ShapeTracker':
        # assert isinstance(arg, tuple) and (len(arg) == len(self.shape) or op == MovementOps.RESHAPE), \
        #     f"arg {arg} for {op} doesn't match dim of shape {self.shape}"
        # dispatch[op](self, arg)
        # return self
        raise NotImplementedError
