import math
import typing as ta

from omlish import cached
from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .dims import Shape
from .dims import ShapeStride
from .dims import Stride
from .ops import MovementOp


def is_contiguous(shape: Shape, stride: Stride) -> bool:
    return all(s1 == s2 or s == 1 for s, s1, s2 in zip(shape, stride, shape.base_stride()))


class View(dc.Data, lang.Final):
    shape: Shape = dc.field(coerce=check.of_isinstance(Shape))
    stride: Stride = dc.field(coerce=check.of_isinstance(Stride))
    offset: int = 0
    mask: ta.Any = None  # FIXME: ta.Optional[ta.Tuple[ta.Tuple[int, int], ...]]

    @cached.property
    def contiguous(self) -> bool:
        return self.offset == 0 and is_contiguous(self.shape, self.stride) and self.mask is None

    @staticmethod
    def of_shape(sh: Shape) -> 'View':
        return View(sh, sh.base_stride())

    @cached.property
    def shape_strides(self) -> ta.Sequence[ShapeStride]:
        return ShapeStride.calc(self.shape, self.stride)


# def merge_views(vm2: View, vm1: View) -> ta.Optional[View]:
#     if vm2.mask:
#         return None  # this isn't supported yet
#     new_strides, new_offset = [], vm2.expr_node(Variable.num(vm1.offset))
#     check,isinstance(new_offset, NumNode)
#     for s, st in zip(vm1.shape, vm1.strides):
#         this_dim = View(vm2.shape, vm2.strides).expr_node(Variable('idx', 0, s - 1) * st)
#         if s == 1:
#             new_strides.append(0)  # all shape 1 can have stride 0
#         elif isinstance(this_dim, NumNode) and this_dim.b == 0:
#             new_strides.append(0)
#         elif isinstance(this_dim, Variable):
#             new_strides.append(1)
#         elif isinstance(this_dim, MulNode) and isinstance(this_dim.a, Variable):
#             new_strides.append(this_dim.b)
#         else:
#             break
#     if len(new_strides) == len(vm1.strides):
#         return View(
#             vm1.shape,
#             tuple(new_strides),
#             new_offset.b,
#             vm1.mask,
#         )
#     return None


class ShapeTracker(lang.Final):
    def __init__(self, shape: ta.Union[Shape, 'ShapeTracker']) -> None:
        super().__init__()

        if isinstance(shape, ShapeTracker):
            self._views = list(shape._views)
        else:
            self._views = [View.of_shape(shape)]

    _views: ta.List[View]

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
        self._views[-1] = View(
            new_shape,
            self._views[-1].stride,
            self._views[-1].offset,
            mask,
        )

    def permute(self, axis: ta.Sequence[int]) -> None:
        check.arg(
            all(isinstance(x, int) and 0 <= x < len(self.shape) for x in axis),
            f'invalid permute {axis} for {self.shape}',
        )
        check.arg(
            len(set(axis)) == len(axis) and len(axis) == len(self.shape),
            f"can't permute {self.shape} with {axis}",
        )
        self._views[-1] = View(
            Shape(self.shape[a] for a in axis),
            Stride(self._views[-1].stride[a] for a in axis),
            self._views[-1].offset,
            tuple(self._views[-1].mask[a] for a in axis) if self._views[-1].mask is not None else None,
        )

    def reshape(self, new_shape: ta.Sequence[int]) -> None:
        if self.shape == new_shape:
            return

        check.arg(
            all(check.isinstance(x, int) > 0 for x in new_shape),
            f"shape must be ints and can't contain 0 or negative numbers {new_shape}"
        )
        check.arg(math.prod(self.shape) == math.prod(new_shape), f"can't reshape {self.shape} -> {new_shape}")

        # check if this is adding or removing 1s (only)
        # NOTE: this is optional, but removes most calls to (expensive!) merge_views (with mask, not optional)
        if tuple(x for x in self.shape if x != 1) == tuple(x for x in new_shape if x != 1):
            old_stride = [y for x, y in zip(self.shape, self._views[-1].stride) if x != 1]
            new_stride = tuple(0 if x == 1 else old_stride.pop(0) for x in new_shape)
            new_mask = None

            if self._views[-1].mask:
                if any(y != (0, 1) for x, y in zip(self.shape, self._views[-1].mask) if x == 1):
                    # mask it all out!
                    new_mask = tuple((0, 0) for _ in new_shape)
                else:
                    old_mask = [y for x, y in zip(self.shape, self._views[-1].mask) if x != 1]
                    new_mask = tuple((0, 1) if x == 1 else old_mask.pop(0) for x in new_shape)

            self._views[-1] = View(
                Shape(new_shape),
                Stride(new_stride),
                self._views[-1].offset,
                new_mask,
            )

            return

        # view = View(new_shape, Shape(new_shape).base_stride())
        # if self.contiguous:
        #     self._views[-1] = view  # NOTE: if it's contiguous it can't have an offset
        # else:
        #     if (merged_view := merge_views(self._views[-1], view)) is not None:
        #         self._views[-1] = merged_view
        #     else:
        #         self._views.append(view)

        raise NotImplementedError

    def movement_op(self, op: MovementOp, arg: ta.Sequence[int]) -> 'ShapeTracker':
        if op != MovementOp.RESHAPE and len(arg) != len(self.shape):
            raise RuntimeError(f'arg {arg} for {op} does not match dim of shape {self.shape}')
        self._movement_op_dispatch[op](self, arg)
        return self

    _movement_op_dispatch: ta.Final[ta.Mapping[MovementOp, ta.Callable]] = {
        MovementOp.EXPAND: expand,
        MovementOp.PERMUTE: permute,
        MovementOp.RESHAPE: reshape,
    }
