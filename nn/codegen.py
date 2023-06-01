import abc
import typing as ta

from omlish import lang

from .lazy import LazyBuffer
from .lazy import LazyOp
from .lazy import map_buffers
from .ops import MovementOp


class Program(lang.Abstract):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def exec(self, bufs: ta.Sequence[LazyBuffer]) -> None:
        raise NotImplementedError


class CodegenOp(lang.Abstract):
    @property
    @abc.abstractmethod
    def key(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def buffers(self) -> ta.Sequence[LazyBuffer]:
        raise NotImplementedError

    @abc.abstractmethod
    def build(self) -> Program:
        raise NotImplementedError


class Codegen(lang.Abstract):
    @abc.abstractmethod
    def op(self, op: LazyOp, output: LazyBuffer) -> CodegenOp:
        raise NotImplementedError


##


class LinearCodegenOp(CodegenOp):
    def __init__(self, op: LazyOp, output: LazyBuffer) -> None:
        super().__init__()

        # NOTE: if there's a RESHAPE, we skip it. the output shape is set from the reduce op or a latebuf
        self._op = op.srcs[0] if op.op == MovementOp.RESHAPE else op

        # get the output buffers
        self._bufs = [output] + dedup(op.buffers)

        # bufs are needed because kernels like f(x) = x + x and f(x, y) = x + y have the same str(ast), but are
        # different kernels. mapping the buffers to integers is required because a-b != b-a (and how would you tell a
        # and b apart?)
        self._key = (
            f'LinearCodegenOp '
            f'op={str(map_buffers({x:i for i,x in enumerate(self._bufs)}, op))} '
            f'bufs={self._bufs}'
        )

    @property
    def key(self) -> str:
        return self._key

    @property
    def buffers(self) -> ta.Sequence[LazyBuffer]:
        return self._bufs

    def build(self) -> Program:
        raise NotImplementedError


class LinearCodegen(Codegen):
    def op(self, op: LazyOp, output: LazyBuffer) -> CodegenOp:
        raise NotImplementedError


##


class CstyleCodegen(LinearCodegen):
    pass
