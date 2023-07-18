import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dispatch

from tinygrad import ops as tg_ops
from tinygrad.helpers import DType as TgDtype
from tinygrad.helpers import dtypes as tg_dtypes
from tinygrad.lazy import LazyBuffer as TgLazyBuffer
from tinygrad.lazy import LazyOp as TgLazyOp
from tinygrad.shape.shapetracker import ShapeTracker as TgShapeTracker

from nn import ops
from nn.buffers import Buffer
from nn.devices import Device
from nn.dims import Shape
from nn.dims import Stride
from nn.dtypes import Dtype
from nn.dtypes import Dtype
from nn.dtypes import Float32
from nn.lazy import Lazy
from nn.raw import RawBuffer
from nn.shapetracker import ShapeTracker
from nn.tensor import Tensor


TgLazy = ta.Union[TgLazyOp, TgLazyBuffer]


class TgConverter:
    @dispatch.method
    def convert(self, obj: ta.Any) -> ta.Any:
        raise TypeError(obj)

    DTYPE_DCT: ta.Final[ta.Mapping[TgDtype, Dtype]] = {
        tg_dtypes.float32: Float32,
    }

    @convert.register
    def convert_tg_dtype(self, dt: TgDtype) -> Dtype:
        return self.DTYPE_DCT[dt]

    OP_CONVERTERS: ta.Final[ta.Mapping[tg_ops.Op, ta.Callable[['TgConverter', TgLazyOp], ops.Op]]] = {
        **{o: (lambda ot: lambda self, op: ot(
            self.convert_tg_lazy(op.src[0]),
        ))(ot) for o, ot in [
            (tg_ops.UnaryOps.NOOP, ops.Nop),
            (tg_ops.UnaryOps.EXP2, ops.Exp2),
            (tg_ops.UnaryOps.LOG2, ops.Log2),
            (tg_ops.UnaryOps.SIN, ops.Sin),
            (tg_ops.UnaryOps.RECIP, ops.Recip),
        ]},
        tg_ops.UnaryOps.CAST: lambda self, op: ops.Cast(
            self.convert_tg_lazy(op.src[0]),
            self.convert_tg_dtype(op.arg),
        ),

        **{o: (lambda ot: lambda self, op: ot(
            self.convert_tg_lazy(op.src[0]),
            self.convert_tg_lazy(op.src[1]),
        ))(ot) for o, ot in [  # noqa
            (tg_ops.BinaryOps.ADD, ops.Add),
            (tg_ops.BinaryOps.SUB, ops.Sub),
            (tg_ops.BinaryOps.MUL, ops.Mul),
            (tg_ops.BinaryOps.DIV, ops.Div),
            (tg_ops.BinaryOps.CMPEQ, ops.CmpEq),
            (tg_ops.BinaryOps.MAX, ops.Maximum),
            (tg_ops.BinaryOps.MOD, ops.Mod),
        ]},

        **{o: (lambda ot: lambda self, op: ot(
            self.convert_tg_lazy(op.src[0]),
            Shape(op.arg),
        ))(ot) for o, ot in [  # noqa
            (tg_ops.ReduceOps.SUM, ops.Sum),
            (tg_ops.ReduceOps.MAX, ops.Max),
        ]},

        tg_ops.MovementOps.RESHAPE: lambda self, op: ops.Reshape(
            self.convert_tg_lazy(op.src[0]),
            Shape(op.arg),
        ),  # noqa
        tg_ops.MovementOps.PERMUTE: lambda self, op: ops.Permute(
            self.convert_tg_lazy(op.src[0]),
            col.seq_of(check.of_isinstance(int))(op.arg),
        ),  # noqa
        tg_ops.MovementOps.EXPAND: lambda self, op: ops.Expand(
            self.convert_tg_lazy(op.src[0]),
            Shape(op.arg),
        ),
    }

    @convert.register
    def convert_tg_lazy_op(self, op: TgLazyOp) -> ops.Op:
        return self.OP_CONVERTERS[op.op](self, op)

    def convert_tg_device(self, dev: str) -> Device:
        raise NotImplementedError

    @convert.register
    def convert_tg_shape_tracker(self, st: TgShapeTracker) -> ShapeTracker:
        # return ShapeTracker(
        #
        # )
        raise NotImplementedError

    @convert.register
    def convert_tg_lazy_buffer(self, buf: TgLazyBuffer) -> Buffer:
        src: ta.Union[ops.Op, RawBuffer]
        if (buf_op := getattr(buf, 'op', None)) is not None:
            src = self.convert_tg_lazy_op(buf_op)
        elif buf.realized is not None:
            raise NotImplementedError
        else:
            raise ValueError(buf)
        return Buffer(
            self.convert_tg_device(buf.device),
            self.convert_tg_shape_tracker(buf.st),
            src,
            self.convert_tg_dtype(buf.dtype),
        )

    def convert_tg_lazy(self, laz: TgLazy) -> Lazy:
        if isinstance(laz, TgLazyOp):
            return self.convert_tg_lazy_op(laz)
        if isinstance(laz, TgLazyBuffer):
            return self.convert_tg_lazy_buffer(laz)
        raise TypeError(laz)


def convert_tg(obj: ta.Any) -> ta.Any:
    return TgConverter().convert(obj)
