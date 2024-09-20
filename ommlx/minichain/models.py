import abc
import dataclasses as dc
import enum
import typing as ta

from omlish import lang


T = ta.TypeVar('T')
U = ta.TypeVar('U')


##


@dc.dataclass(frozen=True)
class Request(lang.Final, ta.Generic[T]):
    v: T


##


class FinishReason(enum.Enum):
    STOP = enum.auto()
    LENGTH = enum.auto()
    TOOL_EXECUTION = enum.auto()
    CONTENT_FILTER = enum.auto()
    OTHER = enum.auto()


@dc.dataclass(frozen=True)
class TokenUsage(lang.Final):
    input: int
    output: int
    total: int


@dc.dataclass(frozen=True)
class Response(lang.Final, ta.Generic[T]):
    v: T

    _: dc.KW_ONLY

    usage: TokenUsage | None = None
    reason: FinishReason | None = None


##


class Model(lang.Abstract, ta.Generic[T, U]):
    @abc.abstractmethod
    def generate(self, request: Request[T]) -> Response[U]:
        raise NotImplementedError
