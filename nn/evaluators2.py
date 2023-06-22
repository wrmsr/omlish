import abc
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dispatch
from omlish import lang

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

        self._raw_bufs_by_op: ta.MutableMapping[ops2.Op, RawBuffer] = col.IdentityKeyDict()

    @abc.abstractmethod
    def _make_raw_buffer(self, obj: T) -> RawBuffer:
        raise NotImplementedError

    @abc.abstractmethod
    def _from_buffer(self, lb: ops2.Buffer) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def _from_raw_buffer(self, rb: RawBuffer) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def _eval(self, op: ops2.Op) -> T:
        raise NotImplementedError

    def eval(self, op: ops2.Op, output: ta.Optional[ops2.Buffer] = None) -> RawBuffer:
        try:
            return self._raw_bufs_by_op[op]
        except KeyError:
            pass

        srcs: ta.List[RawBuffer] = []
        for src in op.sources:
            if isinstance(src, ops2.Op):
                srcs.append(self.eval(src))
            elif isinstance(src, ops2.Buffer):
                srcs.append(self._from_buffer(src))
            else:
                raise TypeError(src)

        ret = self._make_buffer(
            self._fns_by_op[op.op](*(
                    [self._to_underlying(x) for x in srcs] +
                    ([op.arg] if op.arg is not None else [])
            ))
        )

