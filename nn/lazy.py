"""
TODO:
 - encode self._realized <-> self._op w/ case class, invalid state unrepresentable
"""
import math
import typing as ta
import weakref

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
import numpy as np

from .devices import Device
from .devices import cpu_device
from .dims import Shape
from .dtypes import Dtype
from .numpy import NumpyValue
from .ops import BinaryOp
from .ops import LoadOp
from .ops import MovementOp
from .ops import Op
from .ops import ReduceOp
from .ops import UnaryOp
from .raw import RawBuffer
from .raw import RawConst
from .raw import RawCpuBuffer
from .shapetracker import ShapeTracker


class Lazy(lang.Abstract, lang.Sealed):

    def as_op(self) -> 'LazyOp':
        return check.isinstance(self, LazyOp)

    def as_buffer(self) -> 'LazyBuffer':
        return check.isinstance(self, LazyBuffer)


@dc.dataclass(frozen=True)
class LazyOp(Lazy):
    op: Op
    srcs: ta.Sequence[Lazy]
    arg: ta.Any = None

    @property
    def buffers(self) -> ta.Iterator['LazyBuffer']:
        for s in self.srcs:
            if isinstance(s, LazyOp):
                yield from s.buffers
            elif isinstance(s, LazyBuffer):
                yield s

    @property
    def ops(self) -> ta.Iterator['LazyOp']:
        yield self
        for s in self.srcs:
            if isinstance(s, LazyOp):
                yield from s.ops


def map_buffers(srcs: ta.Mapping[Lazy, Lazy], x: LazyOp) -> LazyOp:
    check.isinstance(x, LazyOp)
    if srcs and x in srcs:
        return map_buffers(srcs, srcs[x])  # type: ignore

    return LazyOp(
        x.op,
        tuple(map_buffers(srcs, y) if isinstance(y, LazyOp) else srcs[y] for y in x.srcs),
        x.arg,
    )


class LazyBuffer(Lazy):
    def __init__(
            self,
            device: Device,
            st: ShapeTracker,
            src: ta.Union[LazyOp, RawBuffer],
            dtype: Dtype,
    ) -> None:
        super().__init__()

        self._device = check.isinstance(device, Device)
        self._st = check.isinstance(st, ShapeTracker)
        self._dtype = check.isinstance(dtype, Dtype)

        self._op: ta.Optional[LazyOp] = None
        self._realized: ta.Optional[RawBuffer] = None
        if isinstance(src, LazyOp):
            self._op = src
        elif isinstance(src, RawBuffer):
            self._realized = src
        else:
            raise TypeError(src)

        self._output_buffer: ta.Optional[RawBuffer] = None

        self._children: ta.MutableSet['LazyBuffer'] = weakref.WeakSet()
        if isinstance(src, LazyOp):
            for b in src.buffers:
                b._children.add(self)

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
    def op(self) -> ta.Optional[LazyOp]:
        return self._op

    def get_op(self) -> LazyOp:
        return check.not_none(self._op)

    @property
    def is_realized(self) -> bool:
        return self._realized is not None

    def get_realized(self) -> RawBuffer:
        if self._realized is None:
            raise RuntimeError('Not realized')
        return self._realized

    @property
    def dtype(self) -> Dtype:
        return self._dtype

    @property
    def output_buffer(self) -> ta.Optional[RawBuffer]:
        return self._output_buffer

    def unary_op(self, op: UnaryOp) -> 'LazyBuffer':
        return elementwise_op(op, self)

    def binary_op(self, op: BinaryOp, y: 'LazyBuffer') -> 'LazyBuffer':
        return elementwise_op(op, self, y)

    def reduce_op(self, op: ReduceOp, new_shape: Shape) -> 'LazyBuffer':
        if self.shape == new_shape:
            return self

        srcs = _push_movement_ops([self])

        return create_lazy_buffer(
            self.device,
            new_shape,
            LazyOp(op, tuple(srcs), new_shape),
            self.dtype,
        )

    # shrink -> stride -> permute -> reshape -> pad -> expand
    def movement_op(self: 'LazyBuffer', op: MovementOp, arg: ta.Any) -> 'LazyBuffer':
        if op == MovementOp.RESHAPE and self.shape == arg:
            return self

        # TODO: look into why that copy is needed
        local_st = ShapeTracker(self.shape).movement_op(op, arg)

        # instant nops
        if local_st.contiguous and self.shape == local_st.shape:
            return self

        # two ops in a row is one op. merge them if unresolved
        if self._realized is None and (self_op := self.get_op()).op == op:
            sb = self_op.srcs[0].as_buffer()

            # TODO: why is deleting self from children needed? shouldn't GC do it?
            sb._children.discard(self)

            if op in (MovementOp.RESHAPE, MovementOp.EXPAND):
                return sb.movement_op(op, arg)

            if op == MovementOp.SHRINK:
                return sb.movement_op(
                    op,
                    tuple(
                        (b1 + b2, b1 + e2)
                        for (b1, e1), (b2, e2)
                        in zip(self_op.arg, arg)
                    ),
                )

            if op == MovementOp.PERMUTE:
                return sb.movement_op(op, tuple(self_op.arg[i] for i in arg))

            if op == MovementOp.PAD:
                return sb.movement_op(
                    op,
                    tuple((b1 + b2, e1 + e2) for (b1, e1), (b2, e2) in zip(self_op.arg, arg)),
                )

            if op == MovementOp.STRIDE:
                return sb.movement_op(op, tuple(i * j for i, j in zip(arg, self_op.arg)))

        # some permutes are actually just reshapes
        if op == MovementOp.PERMUTE and local_st.contiguous:
            return self.movement_op(MovementOp.RESHAPE, tuple(self.shape[i] for i in arg))

        # move permutes before expands (always, this is safe)
        if op == MovementOp.PERMUTE and self._realized is None and (self_op := self.get_op()).op == MovementOp.EXPAND:
            sb = self_op.srcs[0].as_buffer()  # FIXME
            sb._children.discard(self)
            return sb \
                .movement_op(MovementOp.PERMUTE, arg) \
                .movement_op(MovementOp.EXPAND, tuple(self_op.arg[a] for a in arg))

        ret = create_lazy_buffer(
            self.device,
            ShapeTracker(self._st).movement_op(op, arg),
            LazyOp(op, (self,), arg),
            self.dtype,
        )

        return ret

    def realize(self) -> 'LazyBuffer':
        if self._realized is not None:
            return self

        self_op = self.get_op()
        if self_op.op == LoadOp.CONTIGUOUS:
            sb = self_op.srcs[0].as_buffer()  # FIXME: cast??
            realized = sb.realize().get_realized()
            if sb._st.contiguous and not isinstance(realized, RawConst) and realized.size == math.prod(self.shape):
                # no need to run an AST, this is already contiguous
                self._realized = realized

        elif self_op.op == LoadOp.FROM:
            raw = self_op.srcs[0].as_buffer().get_realized()
            self._realized = RawCpuBuffer.from_cpu(raw.to_cpu())

        elif self_op.op == LoadOp.EMPTY:
            self._realized = RawCpuBuffer(np.empty(math.prod(self.shape), dtype=self.dtype.np))  # FIXME
        elif self_op.op == LoadOp.CONST:
            self._realized = RawCpuBuffer.from_cpu(np.array(self_op.arg, dtype=self.dtype.np))

        elif self_op.op == BinaryOp.MUL:
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

    def _eval_binary_op(self) -> LazyOp:
        self_op = self.get_op()
        check.isinstance(self_op.op, BinaryOp)

        real_srcs: ta.Dict[LazyBuffer, ta.Optional[Lazy]] = {x: None for x in self_op.buffers}

        intermediate_shape = self.shape
        # reshape all the late ops into the output shape
        # NOTE: these reshapes will return self if they don't change the shape
        for x in real_srcs.keys():
            if real_srcs[x] is None:
                real_srcs[x] = x.movement_op(MovementOp.RESHAPE, intermediate_shape)

        ret = map_buffers({k: check.not_none(v) for k, v in real_srcs.items()}, self_op)
        if intermediate_shape != self.shape:
            return LazyOp(MovementOp.RESHAPE, (ret,), self.shape)
        else:
            return ret

    @staticmethod
    def load_op(
            op: LoadOp,
            shape: Shape,
            dtype: Dtype,
            device: Device,
            arg: ta.Any = None,
            src: ta.Any = None,
    ) -> 'LazyBuffer':
        return create_lazy_buffer(
            device,
            shape,
            LazyOp(op, (src,) if src is not None else (), arg),
            dtype,
        )

    @staticmethod
    def from_cpu(x: np.ndarray) -> 'LazyBuffer':
        return LazyBuffer(
            cpu_device(),
            ShapeTracker(Shape(x.shape)),
            RawCpuBuffer.from_cpu(x),
            Dtype.of_np(x.dtype),
        )

    def cast(self: 'LazyBuffer', arg: Dtype) -> 'LazyBuffer':
        if self.dtype == arg:
            return self
        return elementwise_op(UnaryOp.CAST, self, arg=arg)

    def contiguous(self: 'LazyBuffer') -> 'LazyBuffer':
        if self._realized is None and self.get_op().op == LoadOp.CONTIGUOUS:
            return self  # two CONTIGUOUS in a row is one
        return create_lazy_buffer(
            self.device,
            self.shape,
            LazyOp(LoadOp.CONTIGUOUS, (self,)),
            self.dtype,
        )

    def to_cpu(self) -> NumpyValue:
        realized = self.cast(Dtype.of_np(self.dtype.np)).contiguous().realize().get_realized()
        ret = check.isinstance(realized, RawBuffer).to_cpu().reshape(self.shape)
        return ret

    def const_like(self, val) -> 'LazyBuffer':
        return self.load_op(
            LoadOp.CONST,
            Shape(),
            Dtype.of_np(self.dtype.np),
            self.device,
            arg=val
        ).movement_op(
            MovementOp.RESHAPE,
            (1,) * len(self.shape)
        ).movement_op(
            MovementOp.EXPAND,
            self.shape,
        )


def create_lazy_buffer(
        device: Device,
        shape: ta.Union[ShapeTracker, Shape],
        op: LazyOp,
        dtype: Dtype,
) -> LazyBuffer:
    # FIXME: cache lol
    return LazyBuffer(
        device,
        ShapeTracker.of(shape),
        op,
        dtype,
    )


def elementwise_op(
        op: ta.Union[UnaryOp, BinaryOp],
        *srcs: LazyBuffer,
        arg: ta.Optional[ta.Any] = None,
) -> LazyBuffer:
    check.not_empty(srcs)

    out_device = srcs[0].device
    out_shape = srcs[0].shape
    if op == UnaryOp.CAST:
        out_dtype = check.isinstance(arg, Dtype)
    else:
        out_dtype = srcs[0].dtype  # FIXME: max(x.dtype for x in srcs)

    return create_lazy_buffer(
        out_device,
        ShapeTracker.of(out_shape),
        LazyOp(
            op,
            srcs,
            arg=arg,
        ),
        out_dtype,
    )


def _replace_with_movement_ops(
        y: Lazy,
        ops: ta.List[ta.Tuple[MovementOp, ta.Any]],
) -> 'LazyBuffer':
    if isinstance(y, LazyBuffer):
        for op, arg in ops:
            y = y.movement_op(op, arg)
        return y

    elif isinstance(y, LazyOp):
        check.isinstance(y.op, (BinaryOp, UnaryOp))

        return elementwise_op(
            y.op,  # type: ignore
            *[_replace_with_movement_ops(z, ops) for z in y.srcs],
            arg=y.arg
        )

    else:
        raise TypeError(y)


def _push_movement_ops(srcs: ta.Sequence[LazyBuffer]) -> ta.Sequence[LazyBuffer]:
    new_srcs = []

    for x in srcs:
        mops: ta.List[ta.Tuple[MovementOp, ta.Any]] = []
        bx = x

        # backwalk all the movement ops. don't push PAD or EXPAND
        while (
                bx._realized is None
                and isinstance(bx.op, MovementOp)
                and bx.op.op != MovementOp.EXPAND
                and (
                        bx.op.op != MovementOp.PAD
                        # or SHUFFLE_PAD_OPS
                )
                and len(bx._children) <= 1
        ):
            mops.append((check.isinstance(bx.op.op, MovementOp), bx.op.arg))
            bx = bx.op.srcs[0].as_buffer()

        # NOTE: can't push pads with a div
        if (
                bx._realized is None
                and isinstance(bx.op, BinaryOp)
                and len(bx._children) <= 1
                and len(mops)
                and (
                        all(x[0] != MovementOp.PAD for x in mops) or
                        all(x.op != BinaryOp.DIV for x in bx.op.ops)
                )
        ):
            new_srcs.append(_replace_with_movement_ops(bx.op, mops[::-1]))
        else:
            new_srcs.append(x)

    return tuple(new_srcs)
