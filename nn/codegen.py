import abc
import typing as ta

from omlish import lang

from .lazy import LazyBuffer
from .lazy import LazyOp


class Program(lang.Abstract):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def exec(self, bufs: ta.Sequence[LazyBuffer]) -> None:
        raise NotImplementedError


class OpCodegen(lang.Abstract):
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
    def op(self, op: LazyOp, output: LazyBuffer) -> OpCodegen:
        raise NotImplementedError


##


class LinearCodegen(Codegen):
    def op(self, op: LazyOp, output: LazyBuffer) -> OpCodegen:
        raise NotImplementedError


##


class CstyleCodegen(LinearCodegen):
    pass
