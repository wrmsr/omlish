"""
TODO:
 - SymDims / SymShape / SymStride :|
  - BaseDims? urrgh
"""
import math
import typing as ta

from omlish import cached
from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from . import ops
from . import symbolic as sym
from .dims import Shape
from .dims import ShapeStride
from .dims import Stride


def is_contiguous(shape: Shape, stride: Stride) -> bool:
    return all(s1 == s2 or s == 1 for s, s1, s2 in zip(shape, stride, shape.base_stride()))


class View(dc.Data, lang.Final):
    shape: Shape = dc.field(coerce=check.of_isinstance(Shape))
    stride: Stride = dc.field(coerce=check.of_isinstance(Stride))
    offset: sym.SymInt = 0
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

    def gen_mask_sym(self, idx: sym.Sym, valid: ta.Optional[sym.Sym] = None) -> sym.Sym:
        """~expr_node_mask"""
        ret = [valid] if valid is not None else []
        if self.mask is not None:
            acc = 1
            for ns, (x, y) in reversed(list(zip(self.shape, self.mask))):
                base = (idx // acc) % ns
                ret += [base >= x, base < y]
                acc *= ns
        return sym.and_(ret)

    def idxs_to_idx(self, idxs: ta.Sequence[sym.Sym]) -> sym.Sym:
        check.arg(len(idxs) == len(self.shape))
        acc = 1
        ret = []
        for tidx, d in reversed(list(zip(idxs, self.shape))):
            ret.append(tidx * acc)
            acc *= d
        return sym.sum_(ret)

    # generate an expression if you have a single idx variable
    def gen_sym(self, idx: ta.Optional[sym.Sym] = None) -> sym.Sym:
        """~expr_node"""
        if idx is None:
            idx = sym.var('idx', 0, self.shape.prod)

        ret: ta.List[sym.Sym]
        if self.offset:
            ret = [sym.Num(self.offset) if isinstance(self.offset, int) else self.offset]
        else:
            ret = []

        acc = 1
        for ss in reversed(self.shape_strides):
            ret.append(((idx // acc) % ss.shape) * ss.stride)
            acc *= ss.shape
        return sym.sum_(ret)

    # generate an expression if you have a variable or expression for each index
    def gen_syms(self, idxs: ta.Sequence[sym.Sym]) -> sym.Sym:
        """~expr_idxs"""
        check.arg(len(idxs) == len(self.shape))
        return sym.sum_(
            [sym.Num(self.offset) if isinstance(self.offset, int) else self.offset] + [
                idx * st
                for idx, sh, st in zip(idxs, self.shape, self.stride)
                if sh != 1 and st != 0
            ]
        )


def merge_views(vm2: View, vm1: View) -> ta.Optional[View]:
    if vm2.mask:
        return None  # this isn't supported yet

    mst = ShapeTracker(vm1.shape, [vm2, vm1])
    strides = mst.real_strides()
    if None in strides:
        return None

    return View(
        vm1.shape,
        Stride(strides),
        mst.real_offset(),
        vm1.mask,
    )


def _reshape(view: View, new_shape: Shape) -> ta.Tuple[View, bool]:
    shape = view.shape
    mask = view.mask
    strides = view.stride
    offset = view.offset

    # check if this is adding or removing 1s (only)
    # NOTE: this is optional, but removes most calls to (expensive!) merge_views (with mask, not optional)
    if [x for x in shape if x != 1] == [x for x in new_shape if x != 1]:
        new_strides: ta.List[int] = [y for x, y in zip(shape, strides) if x != 1]
        new_strides_tuple: ta.Tuple[int, ...] = tuple([0 if x == 1 else new_strides.pop(0) for x in new_shape])
        new_mask_tuple = None
        if mask:
            for x, y in zip(shape, mask):
                if x == 1 and y != (0, 1):
                    new_mask_tuple = ((0, 0),) * len(new_shape)
                    break
            else:
                new_mask: ta.List[ta.Tuple[int, int]] = [y for x, y in zip(shape, mask) if x != 1]
                new_mask_tuple = tuple([(0, 1) if x == 1 else new_mask.pop(0) for x in new_shape])
        return View(new_shape, Stride(new_strides_tuple), offset, new_mask_tuple), False

    new_view = View(new_shape, new_shape.base_stride())
    if view.contiguous:
        return new_view, False  # NOTE: if it's contiguous it can't have an offset
    else:
        if (merged_view := merge_views(view, new_view)) is not None:
            return merged_view, False
        else:
            return new_view, True


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
    def views(self) -> ta.Sequence[View]:
        return self._views

    @property
    def shape(self) -> Shape:
        return self.view.shape

    @property
    def stride(self) -> Stride:
        return self.view.stride

    @property
    def size(self) -> int:
        v = self.view
        return math.prod([s for s, st in zip(v.shape, v.stride) if st != 0])

    @property
    def contiguous(self) -> bool:
        return len(self._views) == 1 and self.view.contiguous

    def copy(self) -> 'ShapeTracker':
        return ShapeTracker(self.shape, list(self._views))

    def simplify(self):
        if len(self._views) > 1:
            new_view = merge_views(self._views[-2], self.view)
            if new_view:
                self._views = [*self._views[:-2], new_view]
                self.simplify()

    ##

    def _unsafe_resize(self, arg: ta.Sequence[ta.Tuple[int, int]], mask: ta.Any = None) -> None:
        offset = sum([s * x[0] for s, x in zip(self.views[-1].stride, arg)])
        if self.views[-1].mask is not None:
            # move the old mask
            nmask = tuple([
                (max(mx - ax, 0), min(my - ax, ay - ax))
                for (mx, my), (ax, ay) in zip(self.views[-1].mask, arg)
            ])
            # merge the masks if we have two
            mask = tuple(
                (max(mx1, mx2), min(my1, my2))
                for (mx1, my1), (mx2, my2) in zip(nmask, mask)
            ) if mask is not None else nmask
        self._views[-1] = View(
            tuple([y - x for x, y in arg]),
            self.views[-1].stride,
            self.views[-1].offset + offset,
            mask,
        )

    def pad(self, arg: ta.Sequence[ta.Tuple[int, int]]) -> None:
        check.arg(all((b >= 0 and e >= 0) for b, e in arg) and len(arg) == len(self.shape))
        if any(b or e for b, e in arg):
            zvarg = tuple((-b, s + e) for s, (b, e) in zip(self.shape, arg))
            mask = tuple((b, s + b) for s, (b, _) in zip(self.shape, arg))
            self._unsafe_resize(zvarg, mask=mask)

    def shrink(self, arg: ta.Sequence[ta.Tuple[int, int]]) -> None:
        check.arg(all((b >= 0 and e <= s) for s, (b, e) in zip(self.shape, arg)) and len(arg) == len(self.shape))
        self._unsafe_resize(arg)

    # except for the negative case, you can build this from the others. invertible in the negative case
    def restride(self, mul: ta.Sequence[int]) -> None:
        check.arg(all(isinstance(x, int) and x != 0 for x in mul))
        strides = tuple([z * m for z, m in zip(self.views[-1].stride, mul)])
        new_shape = tuple([(s + (abs(m) - 1)) // abs(m) for s, m in zip(self.views[-1].shape, mul)])
        offset = sum(
            (s - 1) * z
            for s, z, m in zip(self.views[-1].shape, self.views[-1].stride, mul)
            if m < 0
        )
        mask = tuple(
            (
                ((mx if m > 0 else s - my) + (abs(m) - 1)) // abs(m),
                ((my if m > 0 else s - mx) + (abs(m) - 1)) // abs(m),
            )
            for (mx, my), s, m in zip(self.views[-1].mask, self.views[-1].shape, mul)
        ) if self.views[-1].mask is not None else None
        self._views[-1] = View(new_shape, strides, self.views[-1].offset + offset, mask)

    ##

    def expand(self, new_shape: Shape) -> None:
        check.arg(all(
            isinstance(x, int) and (s == x or (s == 1 and st == 0))
            for s, x, st in zip(self.shape, new_shape, self.view.stride)
        ), f"Can't expand {self.shape} into {new_shape}")

        # NOTE: can the mask ever be (0,0)?
        mask = tuple(
            (((0, 0) if m != (0, 1) else (0, ns)) if s != ns else m)
            for m, s, ns in zip(self.view.mask, self.shape, new_shape)
        ) if self.view.mask else None
        self._views[-1] = View.new(
            new_shape,
            self.view.stride,
            offset=self.view.offset,
            mask=mask,
        )

    def permute(self, axis: ta.Sequence[int]) -> None:
        check.arg(
            all(isinstance(x, int) and 0 <= x < len(self.shape) for x in axis),
            f'invalid permute {axis} for {self.shape}',
        )
        check.arg(
            len(set(axis)) == len(axis) and len(axis) == len(self.shape),
            f"Can't permute {self.shape} with {axis}",
        )
        self._views[-1] = View.new(
            Shape(self.shape[a] for a in axis),
            Stride(self.view.stride[a] for a in axis),
            offset=self.view.offset,
            mask=tuple(self.view.mask[a] for a in axis) if self.view.mask is not None else None,
        )

    def reshape(self, new_shape: Shape) -> None:
        if self.views[-1].shape == new_shape:
            return
        check.arg(all(isinstance(x, int) and x > 0 for x in new_shape))
        check.arg(self.shape.prod == new_shape.prod)
        new_view, extra = _reshape(self.views[-1], new_shape)
        if extra:
            self._views.append(new_view)
        else:
            self._views[-1] = new_view

    _movement_op_dispatch: ta.Final[ta.Mapping[ta.Type[ops.MovementOp], ta.Callable]] = {
        ops.Reshape: reshape,
        ops.Permute: permute,
        ops.Expand: expand,
        ops.Pad: pad,
        ops.Shrink: shrink,
        ops.Restride: restride,
    }

    def movement_op(self, op: ta.Type[ops.MovementOp], arg: ta.Any) -> 'ShapeTracker':
        if op != ops.Reshape and len(arg) != len(self.shape):
            raise RuntimeError(f'arg {arg} for {op} does not match dim of shape {self.shape}')
        self._movement_op_dispatch[op](self, arg)
        return self

    ##

    class Sym(ta.NamedTuple):
        idx: sym.Sym
        mask: sym.Sym

    def _gen_sym(self, idx: sym.Sym, valid: sym.Sym) -> Sym:
        """~_expr_idx"""
        for v in reversed(self._views[0:-1]):
            valid = v.gen_mask_sym(idx, valid)
            idx = v.gen_sym(idx)
        return ShapeTracker.Sym(idx, valid)

    def gen_sym(self, idx: ta.Union[sym.Sym, str] = 'idx') -> Sym:
        """~expr_idx"""
        if isinstance(idx, str):
            idx = sym.var(idx, 0, self.shape.prod - 1)
        return self._gen_sym(self.view.gen_sym(idx), self.view.gen_mask_sym(idx))

    def gen_syms(self, idxs: ta.Optional[ta.Sequence[sym.Sym]] = None) -> Sym:
        """~expr_idxs"""
        if idxs is None:
            idxs = [sym.var(f'idx{i}', 0, s - 1) for i, s in enumerate(self.shape)]
        idx = self.views[-1].gen_syms(idxs)
        valid = self.views[-1].gen_mask_sym(self.views[-1].idxs_to_idx(idxs))
        return self._gen_sym(idx, valid)

    # these are multiview strides, value is None if it's not a simple strided dimension
    # TODO: this can be shared code between simplify and merge_views
    def real_offset(self) -> int:
        real_offset, mask = self.gen_sym(sym.var('zero', 0, 0))
        return check.isinstance(real_offset, sym.Num).b

    def real_strides(self, ignore_valid=False) -> ta.Sequence[ta.Optional[int]]:
        if len(self.views) == 1 and self.views[-1].mask is None:
            return self.views[-1].stride

        idxs = [sym.var(f'idx{i}', 0, s - 1) for i, s in enumerate(self.shape)]
        idx, valid = self.gen_syms(idxs)
        ret: ta.List[ta.Optional[int]] = [None] * len(self.shape)

        for this_dim in idx.syms if isinstance(idx, sym.Sum) else [idx]:
            if isinstance(this_dim, sym.Mul) and isinstance(this_dim.a, sym.Var) and this_dim.a in idxs:
                ret[idxs.index(this_dim.a)] = this_dim.b
            elif isinstance(this_dim, sym.Var):
                ret[idxs.index(this_dim)] = 1

        idx_vars, valid_vars = list(idx.vars()), list(valid.vars())
        for i, tidx in enumerate(idxs):
            if tidx in valid_vars and not ignore_valid:
                ret[i] = None
            elif tidx not in idx_vars:
                ret[i] = 0

        return tuple(ret)

    def unit_stride_axes(self) -> ta.Sequence[int]:
        return [i for i, st in enumerate(self.real_strides()) if st == 1]
