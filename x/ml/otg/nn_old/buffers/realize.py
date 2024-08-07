import math
import typing as ta

from omlish import check
from omlish import dispatch
import numpy as np

from .. import ops
from ..lazy import Lazy
from ..raw import RawBuffer
from ..raw import RawConst
from .buffers import Buffer
from .buffers import map_buffers


class Realizer:
    def __init__(self, buf: Buffer) -> None:
        super().__init__()

        self._buf = check.isinstance(buf, Buffer)

    def realize(self) -> tuple[RawBuffer, ops.Op]:
        return self._realize(self._buf.op)

    @dispatch.method
    def _realize(self, op: object) -> tuple[RawBuffer, ops.Op]:
        raise TypeError(op)

    @_realize.register
    def _realize_op(self, op: ops.Op) -> tuple[RawBuffer, ops.Op]:
        for x in op.buffers:
            x.realize()

        realized = self._buf.device.evaluator.eval(op, output=self._buf)  # FIXME: output mutates ugh
        return (realized, op)

    @_realize.register
    def _realize_contiguous(self, op: ops.Contiguous) -> tuple[RawBuffer, ops.Op]:
        sb = op.buf.as_buffer()  # FIXME: cast??
        realized = sb.realize().get_realized()
        if (
                sb._st.contiguous and
                not isinstance(realized, RawConst) and
                realized.size == math.prod(self._buf.shape)
        ):
            # no need to run an AST, this is already contiguous
            return (realized, op)
        else:
            return self._realize(ops.Nop(op.buf))

    @_realize.register
    def _realize_from(self, op: ops.From) -> tuple[RawBuffer, ops.Op]:
        raw = op.srcs[0].as_buffer().get_realized()
        return (self._buf.device.make_raw_buffer(raw.to_cpu()), op)

    @_realize.register
    def _realize_empty(self, op: ops.Empty) -> tuple[RawBuffer, ops.Op]:
        raw = self._buf.device.make_raw_buffer(np.empty(math.prod(self._buf.shape), dtype=self._buf.dtype.np))
        return (raw, op)

    @_realize.register
    def _realize_const(self, op: ops.Const) -> tuple[RawBuffer, ops.Op]:
        # FIXME: supports_constant_folding
        # FIXME: urghh
        # self._realized = self.device.make_raw_buffer(np.array(check.isinstance(self_op, ops.Const).c, dtype=self.dtype.np))  # noqa
        return (RawConst(float(op.c), self._buf.dtype), op)

    @_realize.register
    def _realize_binary_op(self, op: ops.BinaryOp) -> tuple[RawBuffer, ops.Op]:
        real_srcs: ta.Dict[Buffer, ta.Optional[Lazy]] = {x: None for x in op.buffers}

        intermediate_shape = self._buf.shape
        # reshape all the late ops into the output shape
        # NOTE: these reshapes will return self if they don't change the shape
        for x in real_srcs.keys():
            if real_srcs[x] is None:
                real_srcs[x] = x.movement_op(ops.Reshape, intermediate_shape)

        ret = map_buffers({k: check.not_none(v) for k, v in real_srcs.items()}, op)
        if intermediate_shape != self._buf.shape:
            ret_op = ops.Reshape((ret,), self._buf.shape)
        else:
            ret_op = op

        return self._realize_op(ret_op)
