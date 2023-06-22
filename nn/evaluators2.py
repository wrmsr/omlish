import abc
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import lang
import numpy as np

from .raw import RawBuffer
from . import ops2


class Evaluator(lang.Abstract):
    @abc.abstractmethod
    def eval(self, op: ops2.Op, output: ta.Optional[ops2.Buffer] = None) -> RawBuffer:
        raise NotImplementedError


T = ta.TypeVar('T')


class Interpreter(Evaluator, lang.Abstract, ta.Generic[T]):  # noqa

    def __init__(self) -> None:
        super().__init__()

        self._raws_by_op: ta.MutableMapping[ops2.Op, RawBuffer] = col.IdentityKeyDict()

    def _buf_to_raw(self, lb: ops2.Buffer) -> RawBuffer:  # noqa
        return check.isinstance(lb.obj.get_realized(), RawBuffer)

    @abc.abstractmethod
    def _obj_to_raw(self, obj: T) -> RawBuffer:
        raise NotImplementedError

    @abc.abstractmethod
    def _raw_to_obj(self, rb: RawBuffer) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def _eval(self, op: ops2.Op, *objs: T) -> T:
        raise NotImplementedError

    def eval(self, op: ops2.Op, output: ta.Optional[ops2.Buffer] = None) -> RawBuffer:
        try:
            return self._raws_by_op[op]
        except KeyError:
            pass

        srcs: ta.List[RawBuffer] = []
        for src in op.sources:
            if isinstance(src, ops2.Op):
                srcs.append(self.eval(src))
            elif isinstance(src, ops2.Buffer):
                srcs.append(self._buf_to_raw(src))
            else:
                raise TypeError(src)

        out = self._eval(op, *[self._raw_to_obj(src) for src in srcs])
        ret = self._raws_by_op[op] = self._obj_to_raw(out)

        if output is not None and (ob := output.obj.output_buffer) is not None:
            check.state(ob.size == ret.size and ob.dtype == ret.dtype)
            ob._buf = ret._buf  # type: ignore  # FIXME  # noqa
            return ob

        return ret


##


import operator  # noqa

from .raw import RawCpuBuffer  # noqa


class NumpyInterpreter(Interpreter[np.ndarray]):

    def _obj_to_raw(self, obj: np.ndarray) -> RawBuffer:
        return RawCpuBuffer(obj)

    def _raw_to_obj(self, rb: RawBuffer) -> np.ndarray:
        return check.isinstance(check.isinstance(rb, RawCpuBuffer).to_cpu(), np.ndarray)

    _fns_by_op_cls: ta.Final[ta.Mapping[type, ta.Callable[..., np.ndarray]]] = {
        ops2.Exp2: np.exp2,
        ops2.Log2: np.log2,

        ops2.Add: operator.add,
        ops2.Sub: operator.sub,
        ops2.Mul: operator.mul,
        ops2.Div: operator.truediv,
    }

    def _eval(self, op: ops2.Op, *objs: np.ndarray) -> np.ndarray:
        return self._fns_by_op_cls[type(op)](*objs, *op.args)
