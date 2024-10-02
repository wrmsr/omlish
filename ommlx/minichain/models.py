import abc
import enum
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .options import Option
from .options import Options
from .options import UniqueOption


T = ta.TypeVar('T')
U = ta.TypeVar('U')
RequestT = ta.TypeVar('RequestT', bound='Request')
ResponseT = ta.TypeVar('ResponseT', bound='Response')
OptionT = ta.TypeVar('OptionT', bound='Option')


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


##


class RequestOption(Option, lang.Abstract):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class Request(lang.Abstract, ta.Generic[T, OptionT]):
    v: T

    options: Options[OptionT] = Options()

    @classmethod
    def new(cls, v: T, *options: OptionT, **kwargs: ta.Any) -> ta.Self:
        return cls(v, Options(*options), **kwargs)


@dc.dataclass(frozen=True, kw_only=True)
class Response(lang.Abstract, ta.Generic[T]):
    v: T

    usage: TokenUsage | None = None
    reason: FinishReason | None = None


class Model(lang.Abstract, ta.Generic[RequestT, OptionT, ResponseT]):
    @abc.abstractmethod
    def generate(self, request: RequestT) -> ResponseT:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class TopK(RequestOption, UniqueOption, lang.Final):
    k: int


@dc.dataclass(frozen=True)
class Temperature(RequestOption, UniqueOption, lang.Final):
    f: float
