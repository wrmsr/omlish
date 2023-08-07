"""
TODO:
 - encode self._realized <-> self._op w/ case class, invalid state unrepresentable
"""
import typing as ta
import weakref

from omlish import check
from omlish import defs
from omlish import lang
import numpy as np

from ..devices import Device
from ..devices import cpu_device
from ..dims import Shape
from ..dims import Stride
from ..dtypes import Dtype
from ..numpy import NumpyValue
from ..raw import RawBuffer
from ..raw import RawCpuBuffer
from ..shapetracker import ShapeTracker
from ..shapetracker import View
from ..lazy import Lazy
from .. import ops

if ta.TYPE_CHECKING:
    from . import transforms
else:
    transforms = lang.proxy_import('.transforms', __package__)


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

        srcs = transforms.push_movement_ops([self])  # SHUFFLE_MOVEMENT_OPS

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
            return transforms.replace_with_movement_ops(self.get_op(), [(op, arg)])

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

        from .realize import Realizer
        raw, op = Realizer(self).realize()

        self._realized = raw

        # self._op = op
        self._op = None

        return self

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

    srcs = tuple(transforms.push_movement_ops(srcs))  # SHUFFLE_MOVEMENT_OPS

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
