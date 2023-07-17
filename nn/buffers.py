"""
TODO:
 - encode self._realized <-> self._op w/ case class, invalid state unrepresentable
"""
import math
import typing as ta
import weakref

from omlish import check
from omlish import defs
from omlish import dispatch
import numpy as np

from .devices import Device
from .devices import cpu_device
from .dims import Shape
from .dims import Stride
from .dtypes import Dtype
from .numpy import NumpyValue
from .raw import RawBuffer
from .raw import RawConst
from .raw import RawCpuBuffer
from .shapetracker import ShapeTracker
from .shapetracker import View
from .lazy import Lazy
from . import ops


def map_buffers(srcs: ta.Mapping[Lazy, Lazy], x: ops.Op) -> ops.Op:
    check.isinstance(x, ops.Op)
    if srcs and x in srcs:
        return map_buffers(srcs, srcs[x])  # type: ignore

    return type(x)(
        *tuple(map_buffers(srcs, y) if isinstance(y, ops.Op) else srcs[y] for y in x.srcs),
        *x.args,
    )


class Buffer(Lazy):
    def __init__(
            self,
            device: Device,
            st: ShapeTracker,
            src: ta.Union[ops.Op, RawBuffer],
            dtype: Dtype,
    ) -> None:
        super().__init__()

        self._device = check.isinstance(device, Device)
        self._st = check.isinstance(st, ShapeTracker)
        self._dtype = check.isinstance(dtype, Dtype)

        # self._src = check.isinstance(src, (LazyOp, RawBuffer))

        self._op: ta.Optional[ops.Op] = None
        self._realized: ta.Optional[RawBuffer] = None
        if isinstance(src, ops.Op):
            self._op = src
        elif isinstance(src, RawBuffer):
            self._realized = src
        else:
            raise TypeError(src)

        self._output_buffer: ta.Optional[RawBuffer] = None

        self._children: ta.MutableSet['Buffer'] = weakref.WeakSet()
        if isinstance(src, ops.Op):
            for b in src.buffers:
                b._children.add(self)

    defs.repr(
        'device',
        '_op',
        '_realized',
        '_st',
    )

    @property
    def device(self) -> Device:
        return self._device

    @property
    def shape_tracker(self) -> ShapeTracker:
        return self._st

    @property
    def shape(self) -> Shape:
        return self._st.shape

    @property
    def op(self) -> ta.Optional[ops.Op]:
        return self._op

    def get_op(self) -> ops.Op:
        return check.not_none(self._op)

    @property
    def is_realized(self) -> bool:
        return self._realized is not None

    def get_realized(self) -> RawBuffer:
        if self._realized is None:
            raise RuntimeError('Not realized')
        return self._realized

    @property
    def src(self) -> ta.Union[ops.Op, RawBuffer]:
        if self._op is not None:
            return self._op
        elif self._realized is not None:
            return self._realized
        else:
            raise ValueError(self)

    @property
    def dtype(self) -> Dtype:
        return self._dtype

    @property
    def output_buffer(self) -> ta.Optional[RawBuffer]:
        return self._output_buffer

    def unary_op(self, op: ta.Type[ops.UnaryOp]) -> 'Buffer':
        return elementwise_op(op, self)

    def binary_op(self, op: ta.Type[ops.BinaryOp], y: 'Buffer') -> 'Buffer':
        return elementwise_op(op, self, y)

    def reduce_op(self, op: ta.Type[ops.ReduceOp], new_shape: Shape) -> 'Buffer':
        if self.shape == new_shape:
            return self

        srcs = _push_movement_ops([self])  # SHUFFLE_MOVEMENT_OPS

        return create_lazy_buffer(
            self.device,
            new_shape,
            op(*srcs, new_shape),
            self.dtype,
        )

    # shrink -> stride -> permute -> reshape -> pad -> expand
    def movement_op(self: 'Buffer', op: ta.Type[ops.MovementOp], arg: ta.Any) -> 'Buffer':
        if op == ops.Reshape and self.shape == arg:
            return self

        # TODO: look into why that copy is needed
        local_st = ShapeTracker(self.shape).movement_op(op, arg)

        # instant nops
        if local_st.contiguous and self.shape == local_st.shape:
            return self

        # two ops in a row is one op. merge them if unresolved
        if self._realized is None and type(self_op := self.get_op()) == op:
            sb = self_op.srcs[0].as_buffer()

            # TODO: why is deleting self from children needed? shouldn't GC do it?
            sb._children.discard(self)

            if op in (ops.Reshape, ops.Expand):
                return sb.movement_op(op, arg)

            if op == ops.Shrink:
                return sb.movement_op(
                    op,
                    tuple(
                        (b1 + b2, b1 + e2)
                        for (b1, e1), (b2, e2)
                        in zip(check.isinstance(self_op, ops.Shrink).bounds, arg)
                    ),
                )

            if op == ops.Permute:
                return sb.movement_op(op, tuple(check.isinstance(self_op, ops.Permute).axes[i] for i in arg))

            if op == ops.Pad:
                return sb.movement_op(
                    op,
                    tuple((b1 + b2, e1 + e2) for (b1, e1), (b2, e2) in zip(check.isinstance(self_op, ops.Pad).padding, arg)),  # noqa
                )

            if op == ops.Restride:
                return sb.movement_op(op, tuple(i * j for i, j in zip(arg, check.isinstance(self_op, ops.Restride).stride)))  # noqa

        # some permutes are actually just reshapes
        if op == ops.Permute and local_st.contiguous:
            return self.movement_op(ops.Reshape, Shape(self.shape[i] for i in arg))

        # move permutes before expands (always, this is safe)
        if op == ops.Permute and self._realized is None and type(self_op := self.get_op()) == ops.Expand:
            sb = self_op.srcs[0].as_buffer()  # FIXME
            sb._children.discard(self)
            return sb \
                .movement_op(ops.Permute, arg) \
                .movement_op(ops.Expand, Shape(check.isinstance(self_op, ops.Expand).new_shape[a] for a in arg))

        # if this MovementOp is being applied to a BinaryOp, apply the MovementOp to all the BinaryOp inputs instead.
        if (
                # SHUFFLE_MOVEMENT_OPS and
                self._realized is None and
                isinstance(self.get_op(), ops.BinaryOp) and
                (
                        op in (ops.Shrink, ops.Restride, ops.Permute) or
                        (op == ops.Reshape and isinstance(self.get_op(), ops.UnaryOp))
                )
                and len(self._children) == 0
        ):
            return _replace_with_movement_ops(self.get_op(), [(op, arg)])

        ret = create_lazy_buffer(
            self.device,
            ShapeTracker(self._st).movement_op(op, arg),
            op(self, arg),
            self.dtype,
        )

        return ret

    def ternary_op(self, op: ta.Type[ops.TernaryOp], y: 'Buffer', z: 'Buffer') -> 'Buffer':
        return elementwise_op(op, self, y, z)

    def realize(self) -> 'Buffer':
        if self._realized is not None:
            return self

        self_op = self.get_op()

        if isinstance(self_op, ops.Contiguous):
            sb = self_op.buf.as_buffer()  # FIXME: cast??
            realized = sb.realize().get_realized()
            if (
                    sb._st.contiguous and
                    not isinstance(realized, RawConst) and
                    realized.size == math.prod(self.shape)
            ):
                # no need to run an AST, this is already contiguous
                self._realized = realized
            else:
                self._op = ops.Nop(self_op.buf)

        elif isinstance(self_op, ops.From):
            raw = self_op.srcs[0].as_buffer().get_realized()
            self._realized = self.device.make_raw_buffer(raw.to_cpu())

        elif isinstance(self_op, ops.Empty):
            self._realized = self.device.make_raw_buffer(np.empty(math.prod(self.shape), dtype=self.dtype.np))  # FIXME

        elif isinstance(self_op, ops.Const):
            # FIXME: supports_constant_folding
            # FIXME: urghh
            # self._realized = self.device.make_raw_buffer(np.array(check.isinstance(self_op, ops.Const).c, dtype=self.dtype.np))  # noqa
            self._realized = RawConst(float(self_op.c), self.dtype)

        elif isinstance(self_op, ops.Mul):
            self._op = self._eval_binary_op()

        del self_op  # self._op is possibly reassigned

        ##

        if self._realized is None:
            self_op = self.get_op()
            for x in self_op.buffers:
                x.realize()

            self._realized = self.device.evaluator.eval(self_op, output=self)

        # check.isinstance(self.get_realized(), (RawConst, Device[self.device].buffer)),
        #     f"device mismatch on realized got {type(self.realized)} expected {self.device}")

        # no need to keep the op after realization
        self._op = None

        return self

    def _eval_binary_op(self) -> ops.Op:
        self_op = self.get_op()
        check.isinstance(self_op, ops.BinaryOp)

        real_srcs: ta.Dict[Buffer, ta.Optional[Lazy]] = {x: None for x in self_op.buffers}

        intermediate_shape = self.shape
        # reshape all the late ops into the output shape
        # NOTE: these reshapes will return self if they don't change the shape
        for x in real_srcs.keys():
            if real_srcs[x] is None:
                real_srcs[x] = x.movement_op(ops.Reshape, intermediate_shape)

        ret = map_buffers({k: check.not_none(v) for k, v in real_srcs.items()}, self_op)
        if intermediate_shape != self.shape:
            return ops.Reshape((ret,), self.shape)
        else:
            return ret

    @staticmethod
    def load_op(
            op: ta.Type[ops.LoadOp],
            shape: Shape,
            dtype: Dtype,
            device: Device,
            arg: ta.Any = None,
            src: ta.Any = None,
    ) -> 'Buffer':
        return create_lazy_buffer(
            device,
            shape,
            op(*((src,) if src is not None else ()), *([arg] if arg is not None else ())),
            dtype,
        )

    @staticmethod
    def from_cpu(x: np.ndarray) -> 'Buffer':
        return Buffer(
            cpu_device(),
            ShapeTracker(Shape(x.shape), [View(Shape(x.shape), Stride(st // x.itemsize for st in x.strides))]),
            RawCpuBuffer.from_cpu(x),
            Dtype.of_np(x.dtype),
        )

    def cast(self: 'Buffer', arg: Dtype) -> 'Buffer':
        if self.dtype == arg:
            return self
        return elementwise_op(ops.Cast, self, arg=arg)

    def contiguous(self: 'Buffer') -> 'Buffer':
        if self._realized is None and type(self.get_op()) == ops.Contiguous:
            return self  # two CONTIGUOUS in a row is one
        return create_lazy_buffer(
            self.device,
            self.shape,
            ops.Contiguous(self),
            self.dtype,
        )

    def to_cpu(self) -> NumpyValue:
        realized = self.cast(Dtype.of_np(self.dtype.np)).contiguous().realize().get_realized()
        ret = check.isinstance(realized, RawBuffer).to_cpu().reshape(self.shape)
        return ret

    def const_like(self, val) -> 'Buffer':
        return self.load_op(
            ops.Const,
            Shape(),
            Dtype.of_np(self.dtype.np),
            self.device,
            arg=val
        ).movement_op(
            ops.Reshape,
            Shape((1,) * len(self.shape)),
        ).movement_op(
            ops.Expand,
            self.shape,
        )


class Realizer:
    @dispatch.method
    def realize(self, op: ops.Op) -> RawBuffer:
        raise NotImplementedError


def create_lazy_buffer(
        device: Device,
        shape: ta.Union[ShapeTracker, Shape],
        op: ops.Op,
        dtype: Dtype,
) -> Buffer:
    # FIXME: cache lol
    return Buffer(
        device,
        ShapeTracker.of(shape),
        op,
        dtype,
    )


def elementwise_op(
        op: ta.Union[ta.Type[ops.UnaryOp], ta.Type[ops.BinaryOp], ta.Type[ops.TernaryOp]],
        *srcs: Buffer,
        arg: ta.Optional[ta.Any] = None,
) -> Buffer:
    check.not_empty(srcs)

    srcs = tuple(_push_movement_ops(srcs))  # SHUFFLE_MOVEMENT_OPS

    out_device = srcs[0].device
    out_shape = srcs[0].shape
    if op == ops.Cast:
        out_dtype = check.isinstance(arg, Dtype)
    else:
        out_dtype = srcs[0].dtype  # FIXME: max(x.dtype for x in srcs)

    return create_lazy_buffer(
        out_device,
        ShapeTracker.of(out_shape),
        op(*srcs, *([arg] if arg is not None else [])),
        out_dtype,
    )


def _replace_with_movement_ops(
        y: Lazy,
        lst: ta.List[ta.Tuple[ta.Type[ops.MovementOp], ta.Any]],
) -> 'Buffer':
    if isinstance(y, Buffer):
        for op, arg in lst:
            y = y.movement_op(op, arg)
        return y

    elif isinstance(y, ops.Op):
        check.isinstance(y, (ops.BinaryOp, ops.UnaryOp))

        return elementwise_op(
            type(y),  # type: ignore
            *[_replace_with_movement_ops(z, lst) for z in y.srcs],
            *y.args
        )

    else:
        raise TypeError(y)


def _push_movement_ops(srcs: ta.Sequence[Buffer]) -> ta.Sequence[Buffer]:
    new_srcs = []

    for x in srcs:
        mops: ta.List[ta.Tuple[ta.Type[ops.MovementOp], ta.Any]] = []
        bx = x

        # backwalk all the movement ops. don't push PAD or EXPAND
        while (
                bx._realized is None
                and isinstance(bx.op, ops.MovementOp)
                and type(bx.op) != ops.Expand
                and (
                        type(bx.op) != ops.Pad
                        # or SHUFFLE_PAD_OPS
                )
                and len(bx._children) <= 1
        ):
            mops.append((type(check.isinstance(bx.op, ops.MovementOp)), check.single(bx.op.args)))
            bx = bx.op.srcs[0].as_buffer()

        # NOTE: can't push pads past anything where f(0, 0) != 0 or f(0) != 0
        unsafe_pad_ops = {ops.Div, ops.CmpEq, ops.Log2, ops.Exp2, ops.Recip}
        if (
                bx._realized is None
                and isinstance(bx.op, ops.BinaryOp)
                and len(bx._children) <= 1
                and len(mops)
                and (
                all(x[0] != ops.Pad for x in mops) or
                all(type(x) not in unsafe_pad_ops for x in bx.op.ops)
        )
        ):
            new_srcs.append(_replace_with_movement_ops(bx.op, mops[::-1]))
        else:
            new_srcs.append(x)

    return tuple(new_srcs)
