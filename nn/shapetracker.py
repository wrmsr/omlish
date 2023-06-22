import math
import typing as ta

from omlish import cached
from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from . import symbolic as sym
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

    @classmethod
    def new(cls, shape: Shape, stride: Stride, **kwargs: ta.Any) -> 'View':
        return cls(shape, stride.squeeze(shape), **kwargs)

    @cached.property
    def contiguous(self) -> bool:
        return self.offset == 0 and is_contiguous(self.shape, self.stride) and self.mask is None

    @staticmethod
    def of_shape(sh: Shape) -> 'View':
        return View(sh, sh.base_stride())

    @cached.property
    def shape_strides(self) -> ta.Sequence[ShapeStride]:
        return ShapeStride.calc(self.shape, self.stride)

    ##

    def expr_node_mask(self, idx, valid=None) -> sym.Node:
        expr = [valid] if valid is not None else []
        if self.mask is not None:
            acc = 1
            for ns, (x, y) in reversed(list(zip(self.shape, self.mask))):
                base = (idx // acc) % ns
                expr += [base >= x, base < y]
                acc *= ns
        return sym.and_nodes(expr)

    # generate an expression if you have a single idx variable
    def expr_node(self, idx=None) -> sym.Node:
        if idx is None:
            idx = sym.Var("idx", 0, self.shape.prod)
        ret = [sym.Num(self.offset)]
        acc = 1
        for d, s in reversed(self.shape_strides):
            ret.append(((idx // acc) % d) * s)
            acc *= d
        return sym.sum_nodes(ret)


def merge_views(vm2: View, vm1: View) -> ta.Optional[View]:
    if vm2.mask:
        return None  # this isn't supported yet
    mst = ShapeTracker(vm1.shape, [vm2, vm1])
    strides = mst.real_strides()
    if None in strides:
        return None
    return View(
        vm1.shape,
        strides,
        mst.real_offset(),
        vm1.mask,
    )


class ShapeTracker(lang.Final):
    def __init__(
            self,
            shape: ta.Union[Shape, 'ShapeTracker'],
            views: ta.Optional[ta.Sequence[View]] = None,
    ) -> None:
        super().__init__()

        if views is not None:
            # TODO: check against shape? lol
            self._views = list(views)
        elif isinstance(shape, ShapeTracker):
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

    def copy(self) -> 'ShapeTracker':
        return ShapeTracker(self.shape, list(self._views))

    def simplify(self):
        if len(self._views) >= 2:
            new_view = merge_views(self._views[-2], self._views[-1])
            if new_view:
                self._views = [*self._views[:-2], new_view]
                self.simplify()

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
        self._views[-1] = View.new(
            new_shape,
            self._views[-1].stride,
            offset=self._views[-1].offset,
            mask=mask,
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
        self._views[-1] = View.new(
            Shape(self.shape[a] for a in axis),
            Stride(self._views[-1].stride[a] for a in axis),
            offset=self._views[-1].offset,
            mask=tuple(self._views[-1].mask[a] for a in axis) if self._views[-1].mask is not None else None,
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

            self._views[-1] = View.new(
                Shape(new_shape),
                Stride(new_stride),
                offset=self._views[-1].offset,
                mask=new_mask,
            )

            return

        # new_view = View(new_shape, strides_for_shape(new_shape))
        # if view.contiguous:
        #     return new_view, False  # NOTE: if it's contiguous it can't have an offset
        # else:
        #     if (merged_view := merge_views(view, new_view)) is not None:
        #         return merged_view, False
        #     else:
        #         if DEBUG >= 4:
        #             print(f"WARNING: creating new view with reshape {view} -> {new_shape}")
        #         return new_view, True

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

    ##

    def _expr_idx(self, idx, valid):
        for v in reversed(self._views[0:-1]):
            valid = v.expr_node_mask(idx, valid)
            idx = v.expr_node(idx)
        return idx, valid

    def expr_node(self, idx="idx"):
        if isinstance(idx,  str):
            idx = sym.Var(idx, 0, self.shape.prod - 1)
        return self._expr_idx(self._views[-1].expr_node(idx), self._views[-1].expr_node_mask(idx))

    # these are multiview strides, value is None if it's not a simple strided dimension
    # TODO: this can be shared code between simplify and merge_views
    def real_offset(self) -> int:
        real_offset, mask = self.expr_node(sym.Var("zero", 0, 0))
        assert real_offset.__class__ is sym.Num, f"how is the offset not a number? {real_offset} {mask}"
        return real_offset.b

    def real_strides(self) -> ta.Tuple[ta.Optional[int], ...]:
        if len(self._views) == 1:
            return self._views[-1].stride
        ret: ta.List[ta.Optional[int]] = []
        acc, real_offset = 1, self.real_offset()
        for s in reversed(self.shape):
            if s == 1:  # fast path, all shape 1 have stride 0
                ret.append(0)
                continue
            var = sym.Var("idx", 0, s - 1)
            this_dim, _ = self.expr_node(var * acc)
            this_dim -= real_offset
            acc *= s
            # TODO: sometimes a mod here is okay if you are say, reading a float4, since you only care %4
            # if test.__class__ is ModNode and test.b%4 == 0: return check_no_mul(test.a, var)  # removing a mod is okay
            if this_dim.__class__ is sym.Mul and ta.cast(sym.Mul, this_dim).a.__class__ is sym.Var:
                ret.append(this_dim.b)
            elif this_dim.__class__ is sym.Num and this_dim.b == 0:
                ret.append(0)
            elif this_dim.__class__ is sym.Var:
                ret.append(1)
            else:
                ret.append(None)
        return tuple(ret[::-1])
