import math
import typing as ta

from omlish import cached
from omlish import check
from omlish import dataclasses as dc

from .dims import Shape
from .dims import ShapeStride
from .dims import Stride
from .ops import MovementOp


def is_contiguous(shape: Shape, stride: Stride) -> bool:
    return all(s1 == s2 or s == 1 for s, s1, s2 in zip(shape, stride, shape.base_stride()))


@dc.dataclass(frozen=True)
class View:
    shape: Shape
    stride: Stride
    offset: int = 0
    mask: ta.Any = None  # FIXME: ta.Optional[ta.Tuple[ta.Tuple[int, int], ...]]

    @cached.property
    def contiguous(self) -> bool:
        return self.offset == 0 and is_contiguous(self.shape, self.stride) and self.mask is None

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

    @property
    def contiguous(self) -> bool:
        return len(self._views) == 1 and self._views[-1].contiguous

    def expand(self, new_shape: Shape) -> None:
        check.arg(all(
            isinstance(x, int) and (s == x or (s == 1 and st == 0))
            for s, x, st in zip(self.shape, new_shape, self._views[-1].stride)
        ), f"can't expand {self.shape} into {new_shape}")

        # NOTE: can the mask ever be (0,0)?
        mask = tuple(
            (((0, 0) if m != (0, 1) else (0, ns)) if s != ns else m)
            for m, s, ns in zip(self._views[-1].mask, self.shape, new_shape)
        ) if self._views[-1].mask else None
        self._views[-1] = View(new_shape, self._views[-1].stride, self._views[-1].offset, mask)

    def movement_op(self, op: MovementOp, arg: Shape) -> 'ShapeTracker':
        if op != MovementOp.RESHAPE and len(arg) != len(self.shape):
            raise RuntimeError(f'arg {arg} for {op} does not match dim of shape {self.shape}')
        if op == MovementOp.EXPAND:
            self.expand(arg)
        else:
            raise TypeError(op)
        return self
