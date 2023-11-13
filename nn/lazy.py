from __future__ import annotations

import functools
import math
import operator
import sys
import typing as ta
import weakref

from omlish import collections as col
import numpy as np

from . import ops
from .dtypes import DType
from .dtypes import dtypes
from .execution import ConstBuffer
from .execution import MemBuffer
from .execution import ScheduleItem
from .helpers import all_int
from .helpers import flatten
from .helpers import getenv
from .helpers import merge_dicts
from .helpers import prod
from .ops import LazyOp
from .runtime.lib import RawBuffer
from .runtime.ops_cpu import RawNumpyBuffer
from .shape.shapetracker import ShapeTracker
from .shape.shapetracker import get_contraction
from .shape.symbolic import Variable
from .shape.symbolic import sint


# lazy can recurse a lot
sys.setrecursionlimit(10000)


OPT = getenv("OPT", 2)
LAZYCACHE = getenv("LAZYCACHE", 1)

# TODO: movement ops that only change shape are really nops. treat them as such
REMOVE_MOVEMENT_NOPS = OPT >= 1
MERGE_ELEMENTWISE_INTO_REDUCE = OPT >= 1
SHUFFLE_MOVEMENT_OPS = OPT >= 1
MERGE_ELEMENTWISE_OPS = OPT >= 1
MERGE_ONE_REDUCE_INTO_ELEMENTWISE = OPT >= 2
SHUFFLE_PAD_OPS = OPT >= 2
PUSH_PERMUTES = OPT >= 3
PUSH_CONTIGUOUS = OPT >= 3
PUSH_RESHAPES = OPT >= 4


# **** ast fixing functions ****


def _ast_reduceops(op: LazyOp) -> LazyOp:
    # TODO: this can also corealize a binary op after the reduce, not just before
    src = op.src[0]
    if not src.realized:
        assert isinstance(src.op, LazyOp), "if not src.realized, then src.op must be a LazyOp"
        if (
            MERGE_ELEMENTWISE_INTO_REDUCE
            and issubclass(src.optype, ops.BinaryOp)
            and len(src.children) <= 1
        ):
            src = src.op
    return type(op)((src,), op.arg)


# this supports late merging an upstream Reduce op and even an Elementwise op above that
def _ast_binaryops(op: LazyOp, shape: tuple[sint, ...]) -> LazyOp:
    real_srcs: dict[LazyBuffer, ta.Optional[ta.Union[LazyOp, LazyBuffer]]] = {
        x: None for x in op.buffers()
    }

    # NOTE: contiguous does not always mean the same size with SHRINK. this is still mergeable but requires more thought
    # how
    # TODO: this can also support late fusion of BinaryOps, required for test_fold_conv_sgd
    psrcs: list[tuple[LazyBuffer, LazyBuffer]] = [
        (k, x)
        for k, x in zip(
            real_srcs.keys(), map(get_movementroot_contiguous, real_srcs.keys())
        )
        if issubclass(x.optype, ops.ReduceOp)
        and not x.realized
        and prod(k.shape) == prod(x.shape)
        and len(x.children) <= 1
        and len(k.children) <= 1
    ]

    intermediate_shape: tuple[sint, ...] = shape
    if MERGE_ONE_REDUCE_INTO_ELEMENTWISE and psrcs:
        psrc = psrcs[0]  # NOTE: right now we can't handle multiple, as we'd have to check for loop
        if issubclass(psrc[1].optype, ops.ReduceOp):
            top = _ast_reduceops(psrc[1].op)

        real_srcs[psrc[0]] = top
        real_srcs.update(
            {x: x for x in top.buffers()}
        )  # the reduce op buffers are not modified

        # if the ReduceOp is followed by a reshape, we push this reshape before all the ElementwiseOp inputs
        if psrc[0].shape != psrc[1].shape:
            intermediate_shape = psrc[1].shape
            assert psrc[0].shape == shape, f"shape mismatch {psrc[0].shape} != {shape}"

    # reshape all the late ops into the output shape
    # NOTE: these RESHAPEs will return self if they don't change the shape
    for x in real_srcs.keys():
        if real_srcs[x] is None:
            real_srcs[x] = x.reshape(intermediate_shape)

    # NOTE: cast the type to remove the Optional
    ast = op.map_buffers(ta.cast(dict[LazyBuffer, ta.Union[LazyOp, LazyBuffer]], real_srcs))

    return (
        ops.Reshape((ast,), shape)
        if intermediate_shape != shape
        else ast
    )


def _replace_bufferops(op: LazyOp) -> tuple[LazyOp, list[LazyBuffer]]:
    replacements: dict[LazyBuffer, LazyOp] = {}
    base_bufs = col.unique([x.base for x in op.buffers() if not x.is_unrealized_const()])
    for x in op.buffers():
        st = x.st.simplify().unbind()
        if x.base in base_bufs:
            replacements[x] = ops.Mem((), MemBuffer(base_bufs.index(x.base) + 1, x.dtype, st))
        elif not x.realized and isinstance(x.base.op, ops.LoadConst):
            replacements[x] = ops.Const((), ConstBuffer(float(x.base.op.arg), x.dtype, st))
        else:
            raise NotImplementedError(f"not handled {x}")
    return (op.src[0] if isinstance(op, ops.Reshape) else op).map_buffers(replacements), base_bufs


# **** lazy operations ****


def get_single_root(root: LazyBuffer) -> LazyBuffer:
    return (
        get_single_root(root.op.src[0])
        if getattr(root, "op", None) and len(root.op.src) == 1
        and isinstance(root.op.src[0], LazyBuffer)
        else root
    )


def get_movementroot(root: LazyBuffer, allow_contiguous=False) -> LazyBuffer:
    return (
        get_movementroot(ta.cast(LazyBuffer, root.op.src[0]), allow_contiguous)
        if not root.realized
        and (
            issubclass(root.optype, ops.MovementOp)
            or (
                isinstance(root.op, ops.Contiguous)
                and allow_contiguous
                and root.op.src[0].st.contiguous
            )
        )
        else root
    )


def get_movementroot_contiguous(x: LazyBuffer) -> LazyBuffer:
    return (
        get_movementroot_contiguous(ta.cast(LazyBuffer, x.op.src[0]))
        if not x.realized and isinstance(x.op, ops.Contiguous)
        else (
            get_movementroot(x, True)
            if issubclass(x.optype, ops.MovementOp) and x.st.contiguous
            else x
        )
    )


def vars_from_ast(ast: LazyOp) -> list[Variable]:
    return col.unique(
        functools.reduce(
            operator.add,
            [
                x.arg.st.vars()
                for x in ast.get_lazyops()
                if isinstance(x, ops.BufferOp)
            ],
            [],
        ),
    )


lazycache: weakref.WeakValueDictionary = weakref.WeakValueDictionary()


def create_lazybuffer(
    device: str,
    st: ShapeTracker,
    op: LazyOp,
    dtype: DType,
    base: ta.Optional[LazyBuffer] = None,
):
    # fromcpu aren't cached
    if not LAZYCACHE or (
        isinstance(op, ops.LoadOp) and
        type(op) in {ops.Empty, ops.Rand, ops.LoadConst}
    ):
        return LazyBuffer(device, st, op, dtype, base=base)

    # wop is the deduping key. i feel this used to compare more deeply
    wop = (
        device,
        dtype,
        weakref.ref(op),
        weakref.ref(base) if base else None,
    )
    if wop in lazycache:
        for x in op.buffers():
            x.children.add(lazycache[wop])
        return lazycache[wop]

    lazycache[wop] = ret = LazyBuffer(
        device, st, op, dtype, base=base
    )
    return ret


UNSAFE_PAD_OPS = {
    ops.Div,
    ops.CmpLt,
    ops.Log2,
    ops.Exp2,
    ops.Recip,
}


class LazyBuffer:

    def __init__(
        self,
        device: str,
        st: ShapeTracker,
        op: LazyOp,
        dtype: DType,
        src: ta.Optional[RawBuffer] = None,
        base: ta.Optional[LazyBuffer] = None,
    ) -> None:
        super().__init__()

        self.st: ShapeTracker = st
        self.device = device
        self.shape = self.st.shape
        self._dtype = dtype
        self._realized: ta.Optional[RawBuffer] = src
        self.output_buffer: ta.Optional[RawBuffer] = None  # TODO: do we really need this? or can we just use realized
        # TODO: does children have to be a ref count instead of a set? can a Buffer be a double child?
        self.children: weakref.WeakSet = weakref.WeakSet()
        self.views: weakref.WeakSet = weakref.WeakSet()
        # NOTE: op should be read only after construction of LazyBuffer. it is now with schedule
        self.op: LazyOp = op
        self.optype = type(op)
        for x in op.buffers():
            x.children.add(self)
        assert (
            not isinstance(op, ops.MovementOp) or (base is not None and not issubclass(base.optype, ops.MovementOp))
        ), "MovementOps must be based"
        self._base = base
        if base:
            base.views.add(self)
        else:
            assert st.contiguous, "unbased LazyBuffers must be contiguous"

    @property
    def base(self):
        return self._base if self._base is not None else self

    def is_unrealized_const(self) -> bool:
        return not self.realized and (
                isinstance(self.base.op, ops.LoadConst)
        )

    @property
    def realized(self):
        return self.base._realized

    @realized.setter
    def realized(self, val):
        assert self._base is None, "no setting realized of based LazyBuffers"
        self._realized = val

    @property
    def dtype(self):
        return self.base._dtype

    @dtype.setter
    def dtype(self, val):
        assert self._base is None, "no setting dtype of based LazyBuffers"
        self._dtype = val

    def __repr__(self):
        return f"<LB {self.shape} {self.dtype} op={type(self.op).__name__ if hasattr(self, 'op') else self._realized} st={self.st}>"  # noqa

    @property
    def key(self):
        if self.realized:
            return (self.dtype, self.realized.key, self.st)
        return (self.dtype, type(self.op), self.st)

    def _device_extra_args(self) -> dict[str, str]:
        return {"device": self.device.split(":", 1)[1]} if ":" in self.device else {}

    def buffers(self) -> tuple[LazyBuffer, ...]:
        return (self,)

    def map_buffers(self, real_srcs: ta.Mapping[LazyBuffer, ta.Union[LazyBuffer, LazyOp]]):
        return real_srcs.get(self, self)

    def get_lazyops(self) -> list[LazyOp]:
        return []

    # *** scheduling ***

    def schedule(self, seen=None) -> list[ScheduleItem]:
        if seen is None:
            seen = set()
        if self in seen or self.realized or self.is_unrealized_const():
            return []
        seen.add(self)
        if self.base != self:
            return self.base.schedule(seen)

        # rewrite unbased CONTIGUOUS into UnaryOps.NOOP
        op = (
            self.op
            if not isinstance(self.op, ops.Contiguous)
            else ops.Nop(self.op.src)
        )

        if issubclass(self.optype, ops.BinaryOp):
            op = _ast_binaryops(op, self.shape)
        elif issubclass(self.optype, ops.ReduceOp):
            op = _ast_reduceops(op)

        # schedule the AST
        ret = []
        for x in op.buffers():
            ret += x.schedule(seen)

        var_vals = dict(sorted(
            merge_dicts(
                [self.st.var_vals] +
                [buf.st.var_vals for buf in op.buffers()]
            ).items(),
            key=lambda kv: ta.cast(Variable, kv[0]).key),
        )

        # run the ast and log the op
        op, base_bufs = _replace_bufferops(op)
        return ret + [ScheduleItem(op, self, tuple(base_bufs), {k:var_vals[k] for k in vars_from_ast(op)})]

    # *** creation/special ops ***

    @staticmethod
    def loadop(
        op: type[ops.LoadOp], shape, dtype, device, arg=None, src=None,
    ) -> LazyBuffer:
        return create_lazybuffer(
            device,
            ShapeTracker.from_shape(tuple(shape)),
            op(tuple() if src is None else (src,), arg),
            dtype,
        )

    # create a constant with the shape and dtype of self
    def const(self, val: ta.Union[float, int]) -> LazyBuffer:
        # NOTE: dtypes.from_np(self.dtype.np) to deal with image types
        return (
            self.loadop(
                ops.LoadConst,
                tuple(),
                dtypes.from_np(self.dtype.np),
                self.device,
                arg=val,
            )
            .reshape((1,) * len(self.shape))
            .expand(self.shape)
        )

    def copy_to_device(self, device: str) -> LazyBuffer:
        # back off a FROM if it's a double FROM
        if (
                not self.realized
                and isinstance(self.op, ops.From)
                and ta.cast(LazyBuffer, self.op.src[0]).device == device
        ):
            return ta.cast(LazyBuffer, self.op.src[0])
        return LazyBuffer.loadop(
            ops.From,
            self.shape,
            self.dtype,
            device,
            src=self.contiguous(),
        )

    def contiguous(self: LazyBuffer) -> LazyBuffer:
        if not self.realized and isinstance(self.op, ops.Const):
            return self  # two CONTIGUOUS in a row is one

        if self.st.contiguous and self.st.size() == self.base.st.size() and not self.is_unrealized_const():
            # this will turn into nothing, it's based and a copy
            # TODO: based lazybuffers shouldn't take dtype or var_vals, same issue in movementops
            return create_lazybuffer(
                self.device,
                ShapeTracker.from_shape(tuple(self.shape)),
                ops.Contiguous((self,), None),
                self.dtype,
                base=self.base,
            )

        # real contiguous, this will turn into a UnaryOps.NOOP
        return self.loadop(
            ops.Contiguous,
            self.shape,
            self.dtype,
            self.device,
            src=self,
        )

    def contiguous(self: LazyBuffer) -> LazyBuffer:
        if not self.realized and isinstance(self.op, ops.LoadOp) and not isinstance(self.op, ops.LoadConst):
            return self  # all LoadOps are already contiguous (except CONST)
        if self.st.contiguous and self.st.size() == self.base.st.size() and not self.is_unrealized_const():
            # this will turn into nothing, it's based and a copy
            # TODO: based lazybuffers shouldn't take dtype or var_vals, same issue in movementops
            return create_lazybuffer(
                self.device,
                ShapeTracker.from_shape(tuple(self.shape)),
                ops.Contiguous((self,), None),
                self.dtype,
                base=self.base,
            )
        # real contiguous, this will turn into a UnaryOps.NOOP
        return self.loadop(
            ops.Contiguous,
            self.shape,
            self.dtype,
            self.device,
            src=self,
        )

    @staticmethod
    def fromCpu(x: np.ndarray) -> LazyBuffer:
        return LazyBuffer(
            "CPU",
            ShapeTracker.from_shape(x.shape),
            ops.From(()),
            dtypes.from_np(x.dtype),
            RawNumpyBuffer.fromCpu(x),
        )

    def cast(self, dtype: DType, bitcast: bool = False):
        return self.e(ops.Cast, arg=(dtype, bitcast))

    # *** elementwise ops ***

    def e(
        self: LazyBuffer,
        op: ta.Union[type[ops.UnaryOp], type[ops.BinaryOp], type[ops.TernaryOp]],
        *srcs: LazyBuffer,
        arg: ta.Optional[ta.Any] = None,
    ) -> LazyBuffer:
        # srcs includes self
        srcs = (self,) + srcs

        # if we are separated from other binary ops by movement ops, we push those movement ops above those binaryops
        if SHUFFLE_MOVEMENT_OPS:
            srcs = _push_movement_ops(srcs)

        # get outputs now
        out_device, out_shape, out_dtype = (
            srcs[0].device,
            srcs[0].shape,
            max([x.dtype for x in srcs])
            if op != ops.Cast
            else ta.cast(tuple[DType, bool], arg)[0],
        )

        # push all contiguous to the end of BinaryOps. kernels 198 -> 196
        if PUSH_CONTIGUOUS and any(
            not x.realized
            and isinstance(x.op, ops.Contiguous)
            and len(x.op.src[0].children) <= 1
            for x in srcs
        ):
            new_srcs: list[LazyBuffer] = []
            for x in srcs:
                if (
                    not x.realized
                    and isinstance(x.op, ops.Contiguous)
                    and len(x.op.src[0].children) <= 1
                ):
                    x.op.src[0].children.discard(x)
                    new_srcs.append(ta.cast(LazyBuffer, x.op.src[0]))
                else:
                    new_srcs.append(x)
            return new_srcs[0].e(op, *new_srcs[1:], arg=arg).contiguous()

        if MERGE_ELEMENTWISE_OPS:
            # remove the buffers from any (childless) BinaryOps that feed into this
            _srcs = tuple( [x.op if issubclass(x.optype, ops.BinaryOp) and not x.children and not x.realized else x for x in srcs])  # type: ignore
            # TODO: needs general merge limiting
            if (
                    out_device != "WEBGPU"
                    or len(col.unique(x.base for _src in _srcs for x in _src.buffers() if not x.is_unrealized_const())) < 7
            ):
                srcs = _srcs  # type: ignore

        return create_lazybuffer(
            out_device,
            ShapeTracker.from_shape(out_shape),
            op(srcs, arg),
            out_dtype,
        )

    # *** reduce ops ***

    def _reduce_op(
            self: LazyBuffer,
            op: type[ops.ReduceOp],
            new_shape: tuple[sint, ...],
    ) -> LazyBuffer:
        if self.shape == tuple(new_shape):
            return self

        srcs = _push_movement_ops((self,)) if SHUFFLE_MOVEMENT_OPS else (self,)

        unbound_new_shape = tuple(s.unbind()[0] if not isinstance(s, int) else s for s in new_shape)
        return create_lazybuffer(
            self.device,
            ShapeTracker.from_shape(new_shape),
            op(srcs, unbound_new_shape),
            self.dtype,
        )

    def r(self: LazyBuffer, op: type[ops.ReduceOp], new_shape: tuple[sint, ...]) -> LazyBuffer:
        if (
                not all_int(self.shape)
                or prod(self.shape) // prod(new_shape) < getenv("REDUCEOP_SPLIT_THRESHOLD", 32768)
        ):
            return self._reduce_op(op, new_shape)  # The amount of work should be big enough to take the benefit of "2 kernels" approach.

        heuristic, divisor, dim_to_split = max(
            ((divisor := math.gcd(256, old)) / (stride or math.inf), divisor, i)
            for i, (old, new, stride) in enumerate(zip(self.shape, new_shape, self.st.real_strides()))
            if old != new
        )

        if divisor < 16 or heuristic < 0.1:
            return self._reduce_op(op, new_shape)  # Choose largest divisor (>=16) to split on, penalize large strides.

        def splitted_shape(dim_aft_div):
            return (
                self.shape[:dim_to_split] +
                (self.shape[dim_to_split] // divisor,) +
                dim_aft_div +
                self.shape[dim_to_split + 1:]
            )

        return (
            self.reshape(splitted_shape((divisor,)))
            ._reduce_op(op, splitted_shape((1,)))
            .reshape(splitted_shape(()))
            ._reduce_op(op, new_shape)
        )

    # *** movement ops ***

    def _movement_op(
        self,
        st: ShapeTracker,
        op: type[ops.MovementOp],
        arg: ta.Union[tuple[sint, ...], tuple[tuple[sint, sint], ...]],
    ) -> LazyBuffer:
        if (
                SHUFFLE_MOVEMENT_OPS
                and not self.realized
                and issubclass(self.optype, ops.BinaryOp)
                and not self.children
        ):
            if (
                    op in {ops.Shrink, ops.Restride, ops.Permute}
                    or (op == ops.Reshape and (isinstance(self.op, ops.UnaryOp) or PUSH_RESHAPES))
            ):
                return self.op.replace_with_movement_ops([(op, arg)])

        if REMOVE_MOVEMENT_NOPS and not self.realized and st.contiguous:
            # MovementOps aren't stacked any more, they each have one parent, find the root
            root = get_movementroot(self)
            if (
                root.st.contiguous
                and root != self
                and prod(st.shape) == prod(root.shape)
            ):
                return root.reshape(st.shape)

        return create_lazybuffer(
            self.device,
            st,
            op((self,), arg),
            self.dtype,
            base=self.base,
        )

    def reshape(self: LazyBuffer, arg: tuple[sint, ...]) -> LazyBuffer:
        if self.shape == arg:
            return self

        if not self.realized and isinstance(self.op, ops.Reshape):
            assert isinstance(self.op.src[0], LazyBuffer)
            self.op.src[0].children.discard(
                self
            )  # NOTE: this is only required in reshape and when pushing permutes, why??
            return self.op.src[0].reshape(arg)

        return self._movement_op(self.st.reshape(arg), ops.Reshape, arg)

    def pad(self: LazyBuffer, arg: tuple[tuple[int, int], ...]) -> LazyBuffer:
        if all(b == 0 and e == 0 for b, e in arg):
            return self

        if not self.realized and isinstance(self.op, ops.Pad):
            return self.op.src[0].pad(
                tuple(
                    [(b1 + b2, e1 + e2) for (b1, e1), (b2, e2) in zip(self.op.arg, arg)]
                )
            )

        return self._movement_op(self.st.pad(arg), ops.Pad, arg)

    def expand(self: LazyBuffer, arg: tuple[sint, ...]) -> LazyBuffer:
        if self.shape == arg:
            return self

        if not self.realized and isinstance(self.op, ops.Expand):
            return self.op.src[0].expand(arg)

        return self._movement_op(self.st.expand(arg), ops.Expand, arg)

    def permute(self: LazyBuffer, arg: tuple[int, ...]) -> LazyBuffer:
        if arg == tuple(range(len(self.shape))):
            return self

        if not self.realized and issubclass(self.optype, ops.Permute):
            return self.op.src[0].permute(tuple([self.op.arg[i] for i in arg]))

        if SHUFFLE_MOVEMENT_OPS and not self.realized:
            if PUSH_PERMUTES and isinstance(self.op, ops.ReduceOp):
                # reduceops have one buffer input, permute it
                narg = tuple([self.op.arg[a] for a in arg])
                src, rop = self.op.src[0], type(self.op)
                src.children.discard(self)
                del self  # TODO: why doesn't this delete remove it from the children
                return src.permute(arg).r(rop, narg)

            # move permutes before expands (always, this is safe)
            if isinstance(self.op, ops.Expand):
                return (
                    self.op.src[0]
                    .permute(arg)
                    .expand(tuple([self.op.arg[a] for a in arg]))
                )

            # move permutes before reshapes if we can
            if (
                PUSH_PERMUTES
                and isinstance(self.op, ops.Reshape)
                and isinstance(self.op.src[0], LazyBuffer)
            ):
                if shape_idx_groups := get_contraction(
                    self.op.src[0].shape, self.shape
                ):
                    self.op.src[0].children.discard(
                        self
                    )  # NOTE: this is only required in reshape and when pushing permutes, why??
                    return (
                        self.op.src[0]
                        .permute(tuple(flatten(shape_idx_groups[i] for i in arg)))
                        .reshape(self.st.permute(arg).shape)
                    )

        return self._movement_op(self.st.permute(arg), ops.Permute, arg)

    def shrink(self: LazyBuffer, arg: tuple[tuple[sint, sint], ...]) -> LazyBuffer:
        if all(b - a == s for s, (a, b) in zip(self.shape, arg)):
            return self

        if not self.realized and isinstance(self.op, ops.Shrink):
            return self.op.src[0].shrink(
                tuple(
                    [(b1 + b2, b1 + e2) for (b1, _), (b2, e2) in zip(self.op.arg, arg)]
                )
            )
        return self._movement_op(self.st.shrink(arg), ops.Shrink, arg)

    def stride(self: LazyBuffer, arg: tuple[int, ...]) -> LazyBuffer:
        if all(a == 1 for a in arg):
            return self

        if not self.realized and isinstance(self.op, ops.Restride):
            return self.op.src[0].stride(tuple(map(operator.mul, arg, self.op.arg)))

        return self._movement_op(self.st.stride(arg), ops.Restride, arg)

    def replace_with_movement_ops(
        self: LazyBuffer, ops_: list[tuple[type[ops.MovementOp], ta.Any]]
    ) -> LazyBuffer:
        y = self
        for op, arg in ops_:
            y = MOVEMENT_OPS_DISPATCHER[op](y, arg)
        return y


def _push_movement_ops(srcs: tuple[LazyBuffer, ...]) -> tuple[LazyBuffer, ...]:
    new_srcs = []

    for x in srcs:
        mops: list[tuple[type[ops.MovementOp], ta.Any]] = []
        bx = x
        # backwalk all the movement ops. don't push PAD or EXPAND
        while (
            not bx.realized
            and issubclass(bx.optype, ops.MovementOp)
            and not isinstance(bx.op, ops.Expand)
            and (SHUFFLE_PAD_OPS or not isinstance(bx.op, ops.Pad))
            and len(bx.children) <= 1
        ):
            assert isinstance(bx.op, ops.MovementOp)
            mops.append((type(bx.op), bx.op.arg))
            assert isinstance(bx.op.src[0], LazyBuffer)
            bx = bx.op.src[0]

        # NOTE: can't push pads past anything where f(0, 0) != 0 or f(0) != 0
        if (
            mops
            and not bx.realized
            and issubclass(bx.optype, ops.BinaryOp)
            and len(bx.children) <= 1
            and (
                all(y[0] is not ops.Pad for y in mops)
                or all(type(y) not in UNSAFE_PAD_OPS for y in bx.op.get_lazyops())
            )
        ):
            new_srcs.append(bx.op.replace_with_movement_ops(mops[::-1]))
        else:
            new_srcs.append(x)

    return tuple(new_srcs)


MOVEMENT_OPS_DISPATCHER: dict[type[ops.MovementOp], ta.Callable] = {
    ops.Reshape: LazyBuffer.reshape,
    ops.Expand: LazyBuffer.expand,
    ops.Shrink: LazyBuffer.shrink,
    ops.Permute: LazyBuffer.permute,
    ops.Pad: LazyBuffer.pad,
    ops.Restride: LazyBuffer.stride,
}


##


def _tree(x: ta.Union[LazyOp, LazyBuffer], prefix: str = "") -> list[str]:
    if isinstance(x, LazyBuffer):
        if x.realized:
            return [f"━━ realized {x.dtype.name} {x.shape}"]
        return _tree(x.op, "LB ")

    if isinstance(x, LazyOp):
        if len(x.src) == 0:
            return [f"━━ {prefix}{type(x).__name__} {x.arg if x.arg else ''}"]
        lines = [f"━┳ {prefix}{type(x).__name__} {x.arg if x.arg else ''}"]
        childs = [_tree(c) for c in x.src[:]]
        for c in childs[:-1]:
            lines += [f" ┣{c[0]}"] + [f" ┃{l}" for l in c[1:]]
        return lines + [" ┗" + childs[-1][0]] + ["  " + l for l in childs[-1][1:]]

    raise TypeError(x)


def print_tree(x: ta.Union[LazyOp, LazyBuffer]) -> None:
    print("\n".join([f"{str(i).rjust(3)} {s}" for i, s in enumerate(_tree(x))]))
