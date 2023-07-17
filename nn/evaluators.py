import abc
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import lang
import numpy as np

from . import ops
from .buffers import Buffer
from .raw import RawBuffer


class Evaluator(lang.Abstract):
    @abc.abstractmethod
    def eval(self, op: ops.Op, output: ta.Optional[Buffer] = None) -> RawBuffer:
        raise NotImplementedError


T = ta.TypeVar('T')


class Interpreter(Evaluator, lang.Abstract, ta.Generic[T]):  # noqa

    def __init__(self) -> None:
        super().__init__()

        self._raws_by_op: ta.MutableMapping[ops.Op, RawBuffer] = col.IdentityKeyDict()

    def _buf_to_raw(self, lb: Buffer) -> RawBuffer:  # noqa
        return check.isinstance(lb.get_realized(), RawBuffer)

    @abc.abstractmethod
    def _obj_to_raw(self, obj: T) -> RawBuffer:
        raise NotImplementedError

    @abc.abstractmethod
    def _raw_to_obj(self, rb: RawBuffer) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def _eval(self, op: ops.Op, *objs: T) -> T:
        raise NotImplementedError

    def eval(self, op: ops.Op, output: ta.Optional[Buffer] = None) -> RawBuffer:
        try:
            return self._raws_by_op[op]
        except KeyError:
            pass

        srcs: ta.List[RawBuffer] = []
        for src in op.srcs:
            if isinstance(src, ops.Op):
                srcs.append(self.eval(src))
            elif isinstance(src, Buffer):
                srcs.append(self._buf_to_raw(src))
            else:
                raise TypeError(src)

        out = self._eval(op, *[self._raw_to_obj(src) for src in srcs])
        ret = self._raws_by_op[op] = self._obj_to_raw(out)

        if output is not None and (ob := output.output_buffer) is not None:
            check.state(ob.size == ret.size and ob.dtype == ret.dtype)
            ob._buf = ret._buf  # type: ignore  # FIXME  # noqa
            return ob

        return ret


##


import operator  # noqa

from .numpy import NUMPY_VALUE_TYPES  # noqa
from .numpy import NumpyValue  # noqa
from .raw import RawCpuBuffer  # noqa


def shape_to_axis(old_shape: ta.Sequence[int], new_shape: ta.Sequence[int]) -> ta.Sequence[int]:
    check.arg(len(old_shape) == len(new_shape), 'reduce shapes must have same dimensions')
    return tuple(i for i, (a, b) in enumerate(zip(old_shape, new_shape)) if a != b)


class NumpyInterpreter(Interpreter[NumpyValue]):

    def _obj_to_raw(self, obj: NumpyValue) -> RawBuffer:
        return RawCpuBuffer(obj)

    def _raw_to_obj(self, rb: RawBuffer) -> NumpyValue:
        return check.isinstance(check.isinstance(rb, RawCpuBuffer).to_cpu(), NUMPY_VALUE_TYPES)

    _fns_by_op_cls: ta.Final[ta.Mapping[type, ta.Callable[..., NumpyValue]]] = {
        ops.Exp2: np.exp2,
        ops.Log2: np.log2,

        ops.Add: operator.add,
        ops.Sub: operator.sub,
        ops.Mul: operator.mul,
        ops.Div: operator.truediv,
        ops.CmpEq: lambda x, y: (x == y).astype(np.float32),  # noqa
        ops.Maximum: np.maximum,

        ops.Sum: lambda x, new_shape: (
            x.sum(shape_to_axis(x.shape, new_shape), keepdims=True)
            if tuple(x.shape) != tuple(new_shape) else x[:]
        ),

        ops.Max: lambda x, new_shape: (
            (x.amax if hasattr(x, 'amax') else x.max)(shape_to_axis(x.shape, new_shape), keepdims=True)
            if tuple(x.shape) != tuple(new_shape) else x[:]
        ),

        ops.Reshape: lambda x, arg: x.reshape(arg),
        ops.Permute: lambda x, order: x.transpose(order),
        ops.Expand: np.broadcast_to,
        ops.Pad: np.pad,

        ops.Where: np.where,
    }

    def _eval(self, op: ops.Op, *objs: NumpyValue) -> NumpyValue:
        return self._fns_by_op_cls[type(op)](*objs, *op.args)


##


import math  # noqa

from .codegen import Codegen  # noqa
from .codegen import Program  # noqa
from .raw import RawConst  # noqa


class Compiler(Evaluator):

    def __init__(
            self,
            buffer_cls: ta.Type[RawBuffer],
            codegen: Codegen,
            # synchronize: ta.Callable = lambda: None,
    ) -> None:
        super().__init__()

        self._buffer_cls = check.issubclass(buffer_cls, RawBuffer)
        self._codegen = check.isinstance(codegen, Codegen)

        self._prog_cache: ta.Dict[str, Program] = {}

    def eval(
            self,
            op: ops.Op,
            output: ta.Optional[Buffer] = None,
    ) -> RawBuffer:
        output = check.not_none(output)

        # TODO: ???
        # All movementops do nothing in a Compiled buffer!
        if (
                isinstance(op, ops.MovementOp)
                and isinstance((src0 := op.srcs[0]), Buffer)
                and src0.is_realized  # noqa
        ):
            return src0.get_realized()  # noqa

        # check if we can reuse the output buffer. If it's aliased, don't use it.
        # NOTE: this is pretty wrong actually, who knows where else this buffer is used?
        # FIXME: ?????
        output._realized = output._output_buffer
        if output._realized is not None:
            if isinstance(output._realized, RawConst):
                output._realized = None  # can't assign to RawConst
            for a in op.buffers:
                if a._realized == output._realized and not a.shape_tracker.contiguous:
                    output._realized = None
                    break

        # We don't have an output buffer, we have to create it
        if output._realized is None:
            output._realized = self._buffer_cls(math.prod(output.shape), output.dtype)

        cgop = self._codegen.op(op, output)

        print(cgop.key)
        try:
            prog = self._prog_cache[cgop.key]
        except KeyError:
            prog = self._prog_cache[cgop.key] = cgop.build()
        # prog = self._prog_cache[cgop.key] = cgop.build()

        prog.exec(cgop.buffers)
        return output.get_realized()
