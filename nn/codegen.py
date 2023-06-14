import abc
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import lang

from .lazy import LazyBuffer
from .lazy import LazyOp
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
        self._op = check.isinstance(op.srcs[0], LazyOp) if op.op == MovementOp.RESHAPE else op

        # get the output buffers
        self._bufs = [output, *col.unique(op.buffers)]

        # FIXME: ... lol... formalized keyifier plz - str is right though
        # bufs are needed because kernels like f(x) = x + x and f(x, y) = x + y have the same str(ast), but are
        # different kernels. mapping the buffers to integers is required because a-b != b-a (and how would you tell a
        # and b apart?)
        # self._key = (
        #     f'LinearCodegenOp '
        #     f'op={str(map_buffers({x: i for i, x in enumerate(self._bufs)}, op))} '  # FIXME: oof...
        #     f'bufs={self._bufs}'
        # )
        self._key = '???'

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
        return LinearCodegenOp(op, output)


##


class CStyleCodegenOp(LinearCodegenOp):
    pass


class CstyleCodegen(LinearCodegen):
    def op(self, op: LazyOp, output: LazyBuffer) -> CodegenOp:
        return CStyleCodegenOp(op, output)
